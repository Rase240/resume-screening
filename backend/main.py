import csv
import hashlib
import io
import json
import os
import sqlite3
import uuid
from pathlib import Path

from docx import Document
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from pypdf import PdfReader

from scoring import parse_resume, score

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FILES = DATA / "files"
FILES.mkdir(parents=True, exist_ok=True)
DB = DATA / "folio.db"
MAX_FILE = 10 * 1024 * 1024
WEIGHT_KEYS = {"Required skills", "Preferred skills", "Experience", "Education", "Location", "Language similarity"}
app = FastAPI(title="Folio screening API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, requirements TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY, role_id TEXT NOT NULL REFERENCES roles(id) ON DELETE CASCADE, filename TEXT NOT NULL, sha256 TEXT NOT NULL, file_path TEXT NOT NULL, text TEXT NOT NULL, parsed TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'New', notes TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(role_id, sha256));
        """)
init()

class RoleIn(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=20000)
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    min_experience: float = Field(default=0, ge=0, le=50)
    education: str = ""
    location: str = ""
    work_mode: str = "Hybrid"
    weights: dict[str, int] = {"Required skills":35,"Preferred skills":10,"Experience":15,"Education":10,"Location":5,"Language similarity":25}

class CandidateEdit(BaseModel):
    status: str | None = None
    notes: str | None = None
    text: str | None = None
    parsed: dict | None = None

class BulkStatusEdit(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=50)
    status: str

def role_from(row):
    return {"id": row["id"], **json.loads(row["requirements"]), "title": row["title"], "description": row["description"], "created_at": row["created_at"]}

def get_role(role_id):
    with conn() as c:
        row = c.execute("SELECT * FROM roles WHERE id=?", (role_id,)).fetchone()
    if not row: raise HTTPException(404, "Role not found")
    return role_from(row)

def candidate_from(row, role):
    item = {k: row[k] for k in ["id", "role_id", "filename", "text", "status", "notes", "created_at"]}
    item["parsed"] = json.loads(row["parsed"])
    item["match"] = score(role, item)
    return item

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/roles")
def list_roles():
    with conn() as c: rows = c.execute("SELECT * FROM roles ORDER BY created_at DESC").fetchall()
    return [role_from(r) for r in rows]

@app.post("/roles", status_code=201)
def create_role(body: RoleIn):
    if set(body.weights) != WEIGHT_KEYS or sum(body.weights.values()) != 100 or any(v < 0 for v in body.weights.values()):
        raise HTTPException(422, "Scoring weights must total 100")
    role_id = str(uuid.uuid4())
    info = body.model_dump()
    with conn() as c:
        c.execute("INSERT INTO roles(id,title,description,requirements) VALUES(?,?,?,?)", (role_id, body.title, body.description, json.dumps(info)))
    return get_role(role_id)
