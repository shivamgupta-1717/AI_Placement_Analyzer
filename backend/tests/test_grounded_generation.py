import pytest
from app.services.grounded_generation import (
    GroundedGenerationService,
    verify_citation_grounding
)
from app.services.retrieval_service import RetrievedEvidence

@pytest.fixture
def service():
    return GroundedGenerationService()

def test_explicit_abstention_on_empty_evidence(service):
    result = service.assess_requirement(
        requirement_text="Apache Kafka",
        category="cloud_devops",
        priority="mandatory",
        retrieved_evidence=[]
    )
    assert result.classification == "Not found in resume"
    assert "No relevant resume evidence was retrieved" in result.reasoning
    assert result.is_verified_in_source is True

def test_demonstrated_skill_with_lexical_evidence(service):
    ev = RetrievedEvidence(
        chunk_id="c1",
        snippet="Built microservices using Spring Boot and Java.",
        section_name="Experience",
        page_number=1,
        vector_score=0.92,
        lexical_score=1.0,
        combined_score=0.95,
        has_lexical_match=True
    )
    result = service.assess_requirement(
        requirement_text="Spring Boot",
        category="framework",
        priority="mandatory",
        retrieved_evidence=[ev]
    )
    assert result.classification == "Demonstrated"
    assert "Spring Boot" in result.reasoning
    assert result.is_verified_in_source is True

def test_business_dev_vs_full_stack_dev_semantic_disambiguation(service):
    """
    Ensures 'Business Development' in JD is NOT matched to
    'Full Stack Development' in the resume merely due to the word 'Development'.
    """
    ev = RetrievedEvidence(
        chunk_id="c_tech",
        snippet="Experienced in Full Stack Web Development using React, Node.js, and TypeScript.",
        section_name="Experience",
        page_number=1,
        vector_score=0.45,
        lexical_score=0.0,
        combined_score=0.45,
        has_lexical_match=False
    )

    result = service.assess_requirement(
        requirement_text="Business Development",
        category="soft_skill",
        priority="mandatory",
        retrieved_evidence=[ev]
    )

    assert result.classification == "Not found in resume"
    assert "domain" in result.reasoning.lower()

def test_financial_management_vs_state_management_disambiguation(service):
    """
    Ensures 'Corporate Financial Management' in JD is NOT matched to
    'State management in React with Redux' merely due to the word 'management'.
    """
    ev = RetrievedEvidence(
        chunk_id="c_react",
        snippet="Implemented complex state management in React using Redux Toolkit.",
        section_name="Experience",
        page_number=1,
        vector_score=0.40,
        lexical_score=0.0,
        combined_score=0.40,
        has_lexical_match=False
    )

    result = service.assess_requirement(
        requirement_text="Corporate Financial Management and Budgeting",
        category="responsibility",
        priority="mandatory",
        retrieved_evidence=[ev]
    )

    assert result.classification == "Not found in resume"
    assert "domain" in result.reasoning.lower()

def test_network_design_vs_graphic_design_disambiguation(service):
    """
    Ensures 'Computer Network and Infrastructure Design' in JD is NOT matched to
    'Graphic design and UI wireframes' merely due to the word 'design'.
    """
    ev = RetrievedEvidence(
        chunk_id="c_design",
        snippet="Graphic designer creating marketing banners, flyers, and Figma UI prototypes.",
        section_name="Experience",
        page_number=1,
        vector_score=0.40,
        lexical_score=0.0,
        combined_score=0.40,
        has_lexical_match=False
    )

    result = service.assess_requirement(
        requirement_text="Computer Network and Infrastructure Design",
        category="cloud_devops",
        priority="mandatory",
        retrieved_evidence=[ev]
    )

    assert result.classification == "Not found in resume"
    assert "domain" in result.reasoning.lower()

def test_genuine_whole_line_demonstrated_match(service):
    """
    Verifies that a genuine whole-statement match correctly evaluates to Demonstrated.
    """
    ev = RetrievedEvidence(
        chunk_id="c_api",
        snippet="Architected and built RESTful backend APIs with FastAPI and PostgreSQL.",
        section_name="Experience",
        page_number=1,
        vector_score=0.90,
        lexical_score=0.90,
        combined_score=0.92,
        has_lexical_match=True
    )

    result = service.assess_requirement(
        requirement_text="Design, build, and maintain high-throughput backend APIs with FastAPI and PostgreSQL",
        category="framework",
        priority="mandatory",
        retrieved_evidence=[ev]
    )

    assert result.classification == "Demonstrated"
    assert result.is_verified_in_source is True

def test_citation_grounding_verification():
    source_chunks = [
        "Developed full-stack web applications using React, TypeScript, and Node.js.",
        "Graduated with B.Tech in Computer Science from State University."
    ]

    # Authentic citation
    assert verify_citation_grounding("using React, TypeScript, and Node.js", source_chunks) is True

    # Fabricated / hallucinated citation
    assert verify_citation_grounding("Led a 50-person Kubernetes migration at Netflix saving $2M", source_chunks) is False
