import pytest
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.resume import Resume, ResumeChunk
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_embedding_dimension_and_normalization():
    svc = EmbeddingService(dimension=768)
    vec = svc.get_embedding("Software Engineer proficient in Python and Docker")
    assert len(vec) == 768
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-3)

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert np.isclose(EmbeddingService.cosine_similarity(v1, v2), 1.0)
    assert np.isclose(EmbeddingService.cosine_similarity(v1, v3), 0.0)

def test_retrieval_relevance_and_filtering(test_db):
    embed_svc = EmbeddingService(dimension=768)
    retrieval_svc = RetrievalService(db=test_db, embedding_service=embed_svc)

    # Insert test resume & chunks
    resume = Resume(
        id="res-1",
        filename="john_doe.pdf",
        file_type="application/pdf",
        file_size=1024,
        extracted_text="Experienced with Python and FastAPI."
    )
    test_db.add(resume)

    chunk1 = ResumeChunk(
        id="c1",
        resume_id="res-1",
        chunk_index=0,
        section_name="Skills",
        page_number=1,
        content="Proficient in Python programming and FastAPI REST APIs.",
        token_count=10,
        embedding=embed_svc.get_embedding("Proficient in Python programming and FastAPI REST APIs.")
    )
    chunk2 = ResumeChunk(
        id="c2",
        resume_id="res-1",
        chunk_index=1,
        section_name="Interests",
        page_number=1,
        content="Enjoys trail running, hiking, and landscape photography.",
        token_count=10,
        embedding=embed_svc.get_embedding("Enjoys trail running, hiking, and landscape photography.")
    )
    test_db.add_all([chunk1, chunk2])
    test_db.commit()

    # Query for Python requirement
    results = retrieval_svc.retrieve_evidence_for_requirement(
        resume_id="res-1",
        requirement_text="Python",
        lexical_keywords=["python"],
        category="programming_language"
    )

    assert len(results) > 0
    assert results[0].chunk_id == "c1"
    assert results[0].has_lexical_match is True

    # Irrelevant query should not retrieve hiking for Docker
    docker_results = retrieval_svc.retrieve_evidence_for_requirement(
        resume_id="res-1",
        requirement_text="Docker Containerization Kubernetes",
        lexical_keywords=["docker", "kubernetes"],
        threshold=0.45
    )
    # Hiking chunk must be filtered out by threshold
    assert all(r.chunk_id != "c2" for r in docker_results)
