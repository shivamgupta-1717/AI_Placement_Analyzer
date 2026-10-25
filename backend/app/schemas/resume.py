from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ResumeChunkResponse(BaseModel):
    id: str
    chunk_index: int
    section_name: Optional[str] = None
    page_number: Optional[int] = None
    content: str
    token_count: Optional[int] = None

    class Config:
        from_attributes = True

class ResumePreviewResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    extracted_text_preview: str
    full_text_length: int
    detected_sections: List[str]
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    extracted_text: str
    detected_sections: List[str] = []
    raw_metadata: Dict[str, Any] = {}
    chunks: List[ResumeChunkResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
