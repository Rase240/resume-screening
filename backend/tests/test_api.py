import io
from docx import Document
from fastapi.testclient import TestClient
from main import app

client=TestClient(app)
ROLE={"title":"Test Data Engineer","description":"Build data pipelines in Python and SQL", "required_skills":["Python","SQL"],"preferred_skills":["AWS"],"min_experience":2,"education":"","location":"","work_mode":"Remote"}

def test_full_role_upload_review_export_delete_flow():
    role=client.post('/roles',json=ROLE).json()
    rid=role['id']
    doc=Document();doc.add_paragraph('Casey Sample');doc.add_paragraph('Data Engineer');doc.add_paragraph('casey@example.test');doc.add_paragraph('4 years using Python, SQL, and AWS to build data pipelines.')
    raw=io.BytesIO();doc.save(raw)
    files={'files':('casey.docx',raw.getvalue(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    response=client.post(f'/roles/{rid}/upload',files=files)