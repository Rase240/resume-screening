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