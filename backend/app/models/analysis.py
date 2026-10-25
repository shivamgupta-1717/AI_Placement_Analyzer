import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_description_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transparent score breakdown
    overall_match_score = Column(Float, nullable=True) # None if insufficient evidence
    mandatory_coverage = Column(Float, nullable=True)
    preferred_coverage = Column(Float, nullable=True)
    
    summary = Column(Text, nullable=True)
    limitations = Column(JSON, nullable=True, default=list) # Disclosures of unverified / missing info
    status = Column(String(50), default="completed") # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    skill_assessments = relationship("SkillAssessment", back_populates="analysis", cascade="all, delete-orphan")
    learning_items = relationship("LearningItem", back_populates="analysis", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="analysis", cascade="all, delete-orphan")

class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("job_requirements.id", ondelete="SET NULL"), nullable=True)
    requirement_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(50), nullable=False) # "mandatory" or "preferred"
    
    # Explicit 4-state classification
    # "Demonstrated", "Partially demonstrated", "Not found in resume", "Uncertain"
    classification = Column(String(50), nullable=False)
    confidence = Column(Float, default=1.0)
    reasoning = Column(Text, nullable=False)
    
    analysis = relationship("Analysis", back_populates="skill_assessments")
    citations = relationship("EvidenceCitation", back_populates="skill_assessment", cascade="all, delete-orphan")

class EvidenceCitation(Base):
    __tablename__ = "evidence_citations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_assessment_id = Column(String(36), ForeignKey("skill_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(36), ForeignKey("resume_chunks.id", ondelete="SET NULL"), nullable=True)
    snippet = Column(Text, nullable=False)
    source_section = Column(String(100), nullable=True)
    page_number = Column(String(50), nullable=True)
    similarity_score = Column(Float, nullable=True)
    is_verified_in_source = Column(Boolean, default=True) # Post-verification grounding check

    skill_assessment = relationship("SkillAssessment", back_populates="citations")

class LearningItem(Base):
    __tablename__ = "learning_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    priority = Column(String(50), nullable=False) # "high", "medium", "low"
    why_it_matters = Column(Text, nullable=False)
    prerequisites = Column(JSON, nullable=True, default=list)
    suggested_tasks = Column(JSON, nullable=True, default=list)
    mini_project = Column(Text, nullable=False)
    completion_criterion = Column(Text, nullable=False)
    estimated_duration = Column(String(100), nullable=False)

    analysis = relationship("Analysis", back_populates="learning_items")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    category = Column(String(100), nullable=False) # core_technical, coding_problem, project_deep_dive, scenario_based, behavioral
    difficulty = Column(String(50), nullable=False) # easy, medium, hard
    relevance_rationale = Column(Text, nullable=False)
    source_type = Column(String(100), nullable=False) # "job_requirement", "resume_project", "role_knowledge"
    key_concepts = Column(JSON, nullable=True, default=list)
    answer_guidance = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="interview_questions")
