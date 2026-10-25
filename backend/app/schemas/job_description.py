from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class JobRequirementBase(BaseModel):
    requirement_text: str
    category: str # "programming_language", "framework", "database", "education", "experience", "soft_skill"
    priority: str = "mandatory" # "mandatory" or "preferred"
    is_inferred: bool = False
    context_snippet: Optional[str] = None
    lexical_keywords: List[str] = []

class JobRequirementResponse(JobRequirementBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    experience_level: Optional[str] = None
    raw_text: str = Field(..., min_length=20, max_length=20000, description="Job description text (minimum 20 characters)")

class JobDescriptionResponse(BaseModel):
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    experience_level: Optional[str] = None
    raw_text: str
    requirements: List[JobRequirementResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
