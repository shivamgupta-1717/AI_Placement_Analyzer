from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.analysis import Analysis, SkillAssessment, EvidenceCitation
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisSummaryResponse, EvidenceCitationResponse
from app.services.resume_analyzer import ResumeAnalyzerOrchestrator

router = APIRouter(prefix="/analyses", tags=["Analyses"])

@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: AnalysisCreate,
    db: Session = Depends(get_db)
):
    """
    Initiates a full evidence-grounded RAG analysis comparing an uploaded resume against a job description.
    """
    orchestrator = ResumeAnalyzerOrchestrator(db=db)
    try:
        analysis = orchestrator.run_analysis(
            resume_id=payload.resume_id,
            job_description_raw=payload.job_description_raw,
            job_title=payload.job_title,
            company_name=payload.company_name,
            experience_level=payload.experience_level
        )
        return _format_analysis_response(analysis)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {str(e)}")

@router.get("", response_model=List[AnalysisSummaryResponse])
def list_analyses(db: Session = Depends(get_db)):
    """Lists all historical placement analyses with match score summaries."""
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    summaries = []
    for a in analyses:
        resume = db.query(Resume).filter(Resume.id == a.resume_id).first()
        jd = db.query(JobDescription).filter(JobDescription.id == a.job_description_id).first()
        
        demonstrated = sum(1 for sa in a.skill_assessments if sa.classification == "Demonstrated")
        missing = sum(1 for sa in a.skill_assessments if sa.classification == "Not found in resume")
        partial = sum(1 for sa in a.skill_assessments if sa.classification in ["Partially demonstrated", "Uncertain"])

        summaries.append(AnalysisSummaryResponse(
            id=a.id,
            resume_id=a.resume_id,
            resume_filename=resume.filename if resume else "Unknown Resume",
            job_title=jd.title if jd else "Target Role",
            company_name=jd.company if jd else None,
            overall_match_score=a.overall_match_score,
            mandatory_coverage=a.mandatory_coverage,
            preferred_coverage=a.preferred_coverage,
            demonstrated_count=demonstrated,
            missing_count=missing,
            partial_count=partial,
            created_at=a.created_at
        ))
    return summaries

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Fetches complete analysis details including skill evidence, roadmap, and interview questions."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _format_analysis_response(analysis)

@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Deletes an analysis session and cascade-purges its associated skills, citations, roadmap, and questions."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    db.delete(analysis)
    db.commit()
    return None

@router.get("/{analysis_id}/evidence", response_model=List[EvidenceCitationResponse])
def get_analysis_evidence(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieves all evidence citations and source snippets linked to this analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    
    citations = []
    for sa in analysis.skill_assessments:
        for c in sa.citations:
            citations.append(c)
    return citations

def _format_analysis_response(analysis: Analysis) -> AnalysisResponse:
    jd = analysis.job_description
    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        job_title=jd.title if jd else None,
        company_name=jd.company if jd else None,
        experience_level=jd.experience_level if jd else None,
        overall_match_score=analysis.overall_match_score,
        mandatory_coverage=analysis.mandatory_coverage,
        preferred_coverage=analysis.preferred_coverage,
        summary=analysis.summary,
        limitations=analysis.limitations or [],
        status=analysis.status,
        error_message=analysis.error_message,
        created_at=analysis.created_at,
        skill_assessments=analysis.skill_assessments,
        learning_roadmap=analysis.learning_items,
        interview_questions=analysis.interview_questions
    )
