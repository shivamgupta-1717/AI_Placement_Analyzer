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

    results = retrieval_svc.retrieve_evidence_for_requirement(
        resume_id="res-1",
        requirement_text="Python",
        lexical_keywords=["python"],
        category="programming_language"
    )

    assert len(results) > 0
    assert results[0].chunk_id == "c1"
    assert results[0].has_lexical_match is True

    docker_results = retrieval_svc.retrieve_evidence_for_requirement(
        resume_id="res-1",
        requirement_text="Docker Containerization Kubernetes",
        lexical_keywords=["docker", "kubernetes"],
        threshold=0.45
    )
    assert all(r.chunk_id != "c2" for r in docker_results)

def test_retrieval_does_not_lexically_match_on_generic_word_development(test_db):
    """
    Verifies that 'Business Development' query does NOT get has_lexical_match=True
    against a chunk that only mentions 'Full Stack Development'.
    """
    embed_svc = EmbeddingService(dimension=768)
    retrieval_svc = RetrievalService(db=test_db, embedding_service=embed_svc)

    resume = Resume(
        id="res-fullstack",
        filename="fullstack_resume.pdf",
        file_type="application/pdf",
        file_size=1024,
        extracted_text="Full Stack Web Development intern."
    )
    test_db.add(resume)

    chunk = ResumeChunk(
        id="c_fs",
        resume_id="res-fullstack",
        chunk_index=0,
        section_name="Experience",
        page_number=1,
        content="Full Stack Web Development intern working on React and Node.js.",
        token_count=11,
        embedding=embed_svc.get_embedding("Full Stack Web Development intern working on React and Node.js.")
    )
    test_db.add(chunk)
    test_db.commit()

    results = retrieval_svc.retrieve_evidence_for_requirement(
        resume_id="res-fullstack",
        requirement_text="Business Development",
        category="soft_skill"
    )

    # Even if retrieved as candidate, has_lexical_match MUST be False because 'business' is missing!
    for r in results:
        assert r.has_lexical_match is False
        assert r.lexical_score == 0.0
