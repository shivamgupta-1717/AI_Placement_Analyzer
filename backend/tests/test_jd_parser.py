import pytest
from app.services.jd_parser import JobDescriptionParserService

@pytest.fixture
def parser():
    return JobDescriptionParserService()

def test_empty_jd(parser):
    reqs = parser.parse_job_description("")
    assert reqs == []

def test_structured_jd_parsing(parser):
    jd_text = """
    We are looking for a Software Engineer.
    
    Required Qualifications:
    - 3+ years of experience in software engineering
    - Bachelor's degree in Computer Science
    - Proficiency in Python and PostgreSQL
    - Hands-on experience with Docker
    
    Preferred Qualifications:
    - Experience with Kubernetes and React
    - Familiarity with AWS cloud services
    """
    reqs = parser.parse_job_description(jd_text)
    assert len(reqs) >= 5

    categories = {r.category for r in reqs}
    assert "programming_language" in categories
    assert "database" in categories
    assert "cloud_devops" in categories

    # Verify priority segregation
    python_req = next(r for r in reqs if "python" in r.requirement_text.lower())
    assert python_req.priority == "mandatory"

    k8s_req = next(r for r in reqs if "kubernetes" in r.requirement_text.lower())
    assert k8s_req.priority == "preferred"
