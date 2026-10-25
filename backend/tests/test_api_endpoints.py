import pytest
import os
import pymupdf as fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db

TEST_DB_FILE = "./test_api.db"
if os.path.exists(TEST_DB_FILE):
    try:
        os.remove(TEST_DB_FILE)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data

def test_full_analysis_workflow():
    # 1. Generate in-memory PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "SKILLS\nPython, FastAPI, Docker, PostgreSQL\n\nEXPERIENCE\nSoftware Engineer intern building REST APIs.")
    pdf_bytes = doc.tobytes()
    doc.close()

    # 2. Upload resume
    upload_res = client.post(
        "/api/resumes/upload",
        files={"file": ("candidate_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert upload_res.status_code == 201
    resume_data = upload_res.json()
    resume_id = resume_data["id"]
    assert resume_data["chunk_count"] > 0

    # 3. Create analysis
    analysis_payload = {
        "resume_id": resume_id,
        "job_title": "Backend Python Developer",
        "company_name": "Acme Tech",
        "experience_level": "Campus Placement",
        "job_description_raw": (
            "We are looking for a Backend Developer.\n"
            "Required Qualifications:\n"
            "- Strong proficiency in Python and FastAPI\n"
            "- Experience with PostgreSQL database\n"
            "Preferred Qualifications:\n"
            "- Experience with Docker and Kubernetes"
        )
    }
    create_res = client.post("/api/analyses", json=analysis_payload)
    assert create_res.status_code == 201
    analysis_data = create_res.json()
    analysis_id = analysis_data["id"]

    assert analysis_data["overall_match_score"] is not None
    assert len(analysis_data["skill_assessments"]) > 0
    assert len(analysis_data["interview_questions"]) > 0

    # 4. List analyses
    list_res = client.get("/api/analyses")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Get analysis detail
    get_res = client.get(f"/api/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == analysis_id

    # 6. Regenerate interview questions
    regen_res = client.post(
        f"/api/analyses/{analysis_id}/questions/regenerate",
        json={"difficulty": "hard"}
    )
    assert regen_res.status_code == 200
    new_questions = regen_res.json()
    assert len(new_questions) > 0
    assert all(q["difficulty"] == "hard" for q in new_questions)

    # 7. Delete analysis
    del_res = client.delete(f"/api/analyses/{analysis_id}")
    assert del_res.status_code == 204

    # Confirm cascade deletion
    check_res = client.get(f"/api/analyses/{analysis_id}")
    assert check_res.status_code == 404
