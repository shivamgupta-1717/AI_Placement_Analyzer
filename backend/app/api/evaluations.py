from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.evaluation import EvaluationRun
from app.schemas.evaluation import EvaluationRunResponse, EvaluationTriggerRequest
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["RAG Evaluation"])

@router.post("/run", response_model=EvaluationRunResponse, status_code=status.HTTP_201_CREATED)
def run_evaluation(
    payload: Optional[EvaluationTriggerRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Executes the deterministic RAG evaluation benchmark across 10 labeled test scenarios.
    Calculates Precision@K, Recall@K, Citation Validity, Abstention Rate, and Accuracy.
    """
    evaluator = EvaluationService(db=db)
    try:
        results = evaluator.run_benchmark()
        return results
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Evaluation benchmark failed: {str(e)}")

@router.get("/results", response_model=List[EvaluationRunResponse])
def get_evaluation_results(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieves previous evaluation runs and benchmark results."""
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(limit).all()
    return runs

@router.get("/results/latest", response_model=Optional[EvaluationRunResponse])
def get_latest_evaluation_result(db: Session = Depends(get_db)):
    """Retrieves the most recent evaluation benchmark run."""
    run = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).first()
    if not run:
        # If no run exists yet, automatically execute initial benchmark
        evaluator = EvaluationService(db=db)
        return evaluator.run_benchmark()
    return run
