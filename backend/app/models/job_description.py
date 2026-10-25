import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.vector_type import get_vector_column_type
from app.config import settings

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    experience_level = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    requirements = relationship("JobRequirement", back_populates="job_description", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="job_description", cascade="all, delete-orphan")

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_description_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False) # e.g. "programming_language", "framework", "database", "education", "experience", "soft_skill"
    priority = Column(String(50), nullable=False, default="mandatory") # "mandatory" or "preferred"
    is_inferred = Column(Boolean, default=False)
    context_snippet = Column(Text, nullable=True)
    lexical_keywords = Column(JSON, nullable=True, default=list)

    embedding = Column(get_vector_column_type(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job_description = relationship("JobDescription", back_populates="requirements")
