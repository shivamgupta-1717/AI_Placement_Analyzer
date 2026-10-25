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
    CRITICAL TEST: Ensures 'Business Development' in JD is NOT matched to
    'Full Stack Development' in the resume merely due to the word 'Development'.
    """
    # Suppose retrieval returned a technical chunk mentioning full stack development
    ev = RetrievedEvidence(
        chunk_id="c_tech",
        snippet="Experienced in Full Stack Web Development using React, Node.js, and TypeScript.",
        section_name="Experience",
        page_number=1,
        vector_score=0.45,
        lexical_score=0.0, # 'development' is generic, so distinctive 'business' had 0 lexical match
        combined_score=0.45,
        has_lexical_match=False
    )

    result = service.assess_requirement(
        requirement_text="Business Development",
        category="soft_skill",
        priority="mandatory",
        retrieved_evidence=[ev]
    )

    # Must be 'Not found in resume' - never 'Demonstrated'!
    assert result.classification == "Not found in resume"
    assert "distinct domain" in result.reasoning or "lacks the specific core qualifier" in result.reasoning or "business development" in result.reasoning.lower()

def test_citation_grounding_verification():
    source_chunks = [
        "Developed full-stack web applications using React, TypeScript, and Node.js.",
        "Graduated with B.Tech in Computer Science from State University."
    ]

    # Authentic citation
    assert verify_citation_grounding("using React, TypeScript, and Node.js", source_chunks) is True

    # Fabricated / hallucinated citation
    assert verify_citation_grounding("Led a 50-person Kubernetes migration at Netflix saving $2M", source_chunks) is False
