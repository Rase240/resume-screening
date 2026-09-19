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
