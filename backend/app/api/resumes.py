from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.resume import Resume, ResumeChunk
from app.schemas.resume import ResumeResponse, ResumePreviewResponse
from app.services.document_parser import (
    DocumentParserService,
    DocumentParsingError,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    PasswordProtectedError,
    CorruptedDocumentError,
    EmptyDocumentError,
    ScannedDocumentError
)
from app.services.embedding_service import EmbeddingService
from app.config import settings

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumePreviewResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads and extracts a PDF or DOCX resume document.
    Performs security checks, section detection, semantic chunking, and embedding generation.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename must be provided.")

    contents = await file.read()
    parser = DocumentParserService(max_file_size_bytes=settings.UPLOAD_MAX_FILE_SIZE_BYTES)

    try:
        parse_result = parser.parse_document(file.filename, contents)
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))
    except FileSizeLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))
    except PasswordProtectedError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ScannedDocumentError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (EmptyDocumentError, CorruptedDocumentError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document parsing failed: {str(e)}")

    # Create Resume DB record
    resume = Resume(
        filename=parse_result.filename,
        file_type=parse_result.file_type,
        file_size=parse_result.file_size,
        extracted_text=parse_result.full_text,
        detected_sections=parse_result.detected_sections,
        raw_metadata=parse_result.metadata
    )
    db.add(resume)
    db.flush()

    # Generate embeddings and save chunks
    embedding_svc = EmbeddingService()
    chunk_texts = [c.content for c in parse_result.chunks]
    chunk_embeddings = embedding_svc.get_embeddings(chunk_texts)

    for i, c in enumerate(parse_result.chunks):
        chunk_rec = ResumeChunk(
            resume_id=resume.id,
            chunk_index=c.chunk_index,
            section_name=c.section_name,
            page_number=c.page_number,
            content=c.content,
            token_count=c.token_count,
            embedding=chunk_embeddings[i] if i < len(chunk_embeddings) else None
        )
        db.add(chunk_rec)

    db.commit()
    db.refresh(resume)

    return ResumePreviewResponse(
        id=resume.id,
        filename=resume.filename,
        file_type=resume.file_type,
        file_size=resume.file_size,
        extracted_text_preview=resume.extracted_text[:400] + ("..." if len(resume.extracted_text) > 400 else ""),
        full_text_length=len(resume.extracted_text),
        detected_sections=resume.detected_sections or [],
        chunk_count=len(parse_result.chunks),
        created_at=resume.created_at
    )

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Fetches extracted resume details and its semantic chunks."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume
