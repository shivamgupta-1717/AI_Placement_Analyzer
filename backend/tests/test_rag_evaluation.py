import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.services.evaluation_service import EvaluationService

@pytest.fixture
def eval_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_evaluation_benchmark_run(eval_db):
    evaluator = EvaluationService(db=eval_db)
    results = evaluator.run_benchmark()

    assert results["total_test_cases"] == 10
    assert results["classification_accuracy"] >= 80.0
    assert results["citation_validity_rate"] == 100.0
    assert results["abstention_rate"] >= 80.0
    assert results["unsupported_claim_rate"] <= 10.0
    assert results["schema_validation_rate"] == 100.0
    assert results["end_to_end_success_rate"] == 100.0
    assert len(results["detailed_results"]) == 10
