from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class EvaluationRunResponse(BaseModel):
    id: str
    dataset_version: str
    total_test_cases: int
    precision_at_k: float
    recall_at_k: float
    citation_validity_rate: float
    classification_accuracy: float
    unsupported_claim_rate: float
    abstention_rate: float
    schema_validation_rate: float
    end_to_end_success_rate: float
    detailed_results: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class EvaluationTriggerRequest(BaseModel):
    dataset_version: Optional[str] = "1.0.0"
