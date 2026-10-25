from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class EvidenceCitationResponse(BaseModel):
    id: str
    chunk_id: Optional[str] = None
    snippet: str
    source_section: Optional[str] = None
    page_number: Optional[str] = None
    similarity_score: Optional[float] = None
    is_verified_in_source: bool = True

    class Config:
        from_attributes = True

class SkillAssessmentResponse(BaseModel):
    id: str
    requirement_id: Optional[str] = None
    requirement_text: str
    category: str
    priority: str # "mandatory" | "preferred"
    classification: Literal["Demonstrated", "Partially demonstrated", "Not found in resume", "Uncertain"]
    confidence: float
    reasoning: str
    citations: List[EvidenceCitationResponse] = []

    class Config:
        from_attributes = True

class LearningItemResponse(BaseModel):
    id: str
    skill_name: str
    priority: Literal["high", "medium", "low"]
    why_it_matters: str
    prerequisites: List[str] = []
    suggested_tasks: List[str] = []
    mini_project: str
    completion_criterion: str
    estimated_duration: str

    class Config:
        from_attributes = True

class InterviewQuestionResponse(BaseModel):
    id: str
    question: str
    category: Literal["core_technical", "coding_problem", "project_deep_dive", "scenario_based", "behavioral"]
    difficulty: Literal["easy", "medium", "hard"]
    relevance_rationale: str
    source_type: str # "job_requirement" | "resume_project" | "role_knowledge"
    key_concepts: List[str] = []
    answer_guidance: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisCreate(BaseModel):
    resume_id: str = Field(..., description="UUID of the uploaded resume")
    job_description_raw: str = Field(..., min_length=20, max_length=20000, description="Raw job description text")
    job_title: Optional[str] = Field(None, max_length=150)
    company_name: Optional[str] = Field(None, max_length=150)
    experience_level: Optional[str] = Field(None, max_length=50)

class AnalysisSummaryResponse(BaseModel):
    id: str
    resume_id: str
    resume_filename: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    overall_match_score: Optional[float] = None
    mandatory_coverage: Optional[float] = None
    preferred_coverage: Optional[float] = None
    demonstrated_count: int
    missing_count: int
    partial_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: str
    resume_id: str
    job_description_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    experience_level: Optional[str] = None
    overall_match_score: Optional[float] = None
    mandatory_coverage: Optional[float] = None
    preferred_coverage: Optional[float] = None
    summary: Optional[str] = None
    limitations: List[str] = []
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    skill_assessments: List[SkillAssessmentResponse] = []
    learning_roadmap: List[LearningItemResponse] = []
    interview_questions: List[InterviewQuestionResponse] = []

    class Config:
        from_attributes = True

class InterviewQuestionRegenerateRequest(BaseModel):
    difficulty: Optional[Literal["easy", "medium", "hard", "mixed"]] = "mixed"
    focus_category: Optional[str] = None
