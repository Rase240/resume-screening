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

The score is a **role-specific match estimate**, not an official ATS score. Required and preferred skills use explicit term evidence; experience and education use extracted details. Language similarity combines local word and character n-gram TF-IDF cosine similarity. Names, contact details, and common protected-characteristic labels are excluded from similarity input. Configured weights are normalized across applicable categories. Changing a role or correcting extracted text recalculates scores. No paid API key is required.

The score is a review aid. It does not make hiring decisions, and a reviewer should verify parsing, evidence, and borderline cases.

## Privacy and limitations

This is a local mentor/demo application, not a production multi-user hiring service. It has no login, authorization, audit trail, encryption at rest, or retention policy. Keep it bound to localhost. Text-based PDFs work; scanned PDFs need OCR. Extraction of contact details, education, work history, and years of experience is heuristic.

## Verification

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=backend/vendor:backend OPENBLAS_NUM_THREADS=1 python3 -m pytest backend/tests -q
cd frontend && npm run build
```

The backend tests cover parsing, scoring, role creation, upload, duplicate detection, review updates, bulk status validation, CSV export, file access, and deletion.
