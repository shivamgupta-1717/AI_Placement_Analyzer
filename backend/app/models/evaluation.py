import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON
from app.db.session import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_version = Column(String(50), nullable=False, default="1.0.0")
    total_test_cases = Column(Integer, nullable=False)
    
    # Measured metrics
    precision_at_k = Column(Float, nullable=False)
    recall_at_k = Column(Float, nullable=False)
    citation_validity_rate = Column(Float, nullable=False)
    classification_accuracy = Column(Float, nullable=False)
    unsupported_claim_rate = Column(Float, nullable=False)
    abstention_rate = Column(Float, nullable=False)
    schema_validation_rate = Column(Float, nullable=False)
    end_to_end_success_rate = Column(Float, nullable=False)

    detailed_results = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
