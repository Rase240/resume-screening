# Folio — evidence-led resume screening

Folio is a local, single-user screening workbench. Recruiters define a role, upload PDF or DOCX resumes, inspect extracted details and supporting evidence, and make their own review decisions. The application contains **no bundled sample resumes**.

## Run locally

Requires Python 3.12+, Node.js 18+, and npm. From the project root:

**Windows**:
```cmd
start.bat install
start.bat
```

**Linux / macOS**:
```bash
./start.sh install
./start.sh
```

*(Or use the unified cross-platform runner directly: `python run.py [backend|frontend|install|test]`)*

Open <http://127.0.0.1:3000>. The launcher starts the FastAPI service and Next.js interface together. The browser uses the frontend's same-origin `/api` proxy.

## Workflow

1. Create a role with requirements and scoring weights, or edit an existing role.
2. Drop up to 50 PDF or DOCX resumes into the upload area, or use **Choose resumes**. Each file has a 10 MB limit.
3. Check per-file processing results and correct extracted details where needed.
4. Review the role coverage summary, estimated match scores, requirement evidence, and missing requirements.
5. Use Top 5 / Top 10, search, review queue, required-skill and minimum-score filters, and sorting.
6. Compare candidates, save reviewer notes, and change one or several review statuses.
7. Export the full role ranking to CSV or delete a candidate and their uploaded file.

## Architecture and scoring

- `frontend/`: Next.js 14 and React interface.
- `backend/`: FastAPI, SQLite, PDF/DOCX extraction, and scoring.
- `backend/data/`: local database and uploaded originals, excluded from the project archive.
