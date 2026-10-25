from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.analysis import Analysis, InterviewQuestion
from app.models.resume import Resume
from app.schemas.analysis import InterviewQuestionResponse, InterviewQuestionRegenerateRequest
from app.services.interview_generator import InterviewQuestionGeneratorService

router = APIRouter(prefix="/analyses", tags=["Interview Questions"])

@router.get("/{analysis_id}/questions", response_model=List[InterviewQuestionResponse])
def get_questions(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieves generated role-specific interview questions for an analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis.interview_questions

@router.post("/{analysis_id}/questions/regenerate", response_model=List[InterviewQuestionResponse])
def regenerate_questions(
    analysis_id: str,
    payload: InterviewQuestionRegenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerates interview questions tailored to a specific difficulty level
    ('easy', 'medium', 'hard', 'mixed') without altering previous resume assessments.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # Remove existing questions
    db.query(InterviewQuestion).filter(InterviewQuestion.analysis_id == analysis_id).delete()

    # Re-run generator with new difficulty filter
    generator = InterviewQuestionGeneratorService()
    assessment_dicts = [
        {
            "requirement_text": sa.requirement_text,
            "classification": sa.classification,
            "priority": sa.priority
        }
        for sa in analysis.skill_assessments
    ]

    new_questions = generator.generate_questions(
        skill_assessments=assessment_dicts,
        resume_text=resume.extracted_text,
        job_title=analysis.job_description.title if analysis.job_description else "Software Engineer",
        difficulty_filter=payload.difficulty or "mixed"
    )

    created_questions = []
    for q in new_questions:
        iq = InterviewQuestion(
            analysis_id=analysis.id,
            question=q.question,
            category=q.category,
            difficulty=q.difficulty,
            relevance_rationale=q.relevance_rationale,
            source_type=q.source_type,
            key_concepts=q.key_concepts,
            answer_guidance=q.answer_guidance
        )
        db.add(iq)
        created_questions.append(iq)

    db.commit()
    return created_questions
