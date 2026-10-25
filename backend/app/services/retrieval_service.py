import re
from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.resume import ResumeChunk
from app.services.embedding_service import EmbeddingService
from app.config import settings

@dataclass
class RetrievedEvidence:
    chunk_id: Optional[str]
    snippet: str
    section_name: Optional[str]
    page_number: Optional[int]
    vector_score: float
    lexical_score: float
    combined_score: float
    has_lexical_match: bool


class RetrievalService:
    def __init__(self, db: Session, embedding_service: Optional[EmbeddingService] = None):
        self.db = db
        self.embedding_service = embedding_service or EmbeddingService()

    def retrieve_evidence_for_requirement(
        self,
        resume_id: str,
        requirement_text: str,
        lexical_keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        top_k: int = settings.RETRIEVAL_TOP_K,
        threshold: float = settings.RETRIEVAL_SIMILARITY_THRESHOLD
    ) -> List[RetrievedEvidence]:
        """
        Retrieves top relevant resume chunks for a job requirement using hybrid
        (vector cosine + exact keyword) search, with relevance threshold filtering.
        """
        # Fetch chunks for this resume
        chunks = self.db.query(ResumeChunk).filter(ResumeChunk.resume_id == resume_id).all()
        if not chunks:
            return []

        # Generate query embedding for requirement
        query_vec = self.embedding_service.get_embedding(requirement_text)

        # Build keywords list for lexical matching
        keywords = set()
        if lexical_keywords:
            for kw in lexical_keywords:
                if len(kw.strip()) > 1:
                    keywords.add(kw.strip().lower())
        
        # Add primary requirement words
        for token in re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", requirement_text):
            if token.lower() not in {"and", "the", "for", "with", "must", "have", "preferred", "years", "degree"}:
                keywords.add(token.lower())

        candidates: List[RetrievedEvidence] = []

        for chunk in chunks:
            # 1. Vector similarity
            chunk_vec = chunk.embedding
            vec_score = 0.0
            if chunk_vec:
                vec_score = self.embedding_service.cosine_similarity(query_vec, chunk_vec)
                # Bound between 0 and 1
                vec_score = max(0.0, min(1.0, (vec_score + 1.0) / 2.0))

            # 2. Lexical exact match check
            chunk_lower = chunk.content.lower()
            matched_keywords = [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", chunk_lower)]
            
            lex_score = 0.0
            has_exact = False
            if matched_keywords:
                has_exact = True
                lex_score = min(1.0, len(matched_keywords) / max(1, len(keywords)))

            # Section boost (e.g. if category is programming_language and section is Skills)
            section_boost = 0.0
            if category and chunk.section_name:
                sec_lower = chunk.section_name.lower()
                if category in ["programming_language", "framework", "database"] and "skill" in sec_lower:
                    section_boost = 0.05
                elif category in ["experience", "responsibility"] and "experience" in sec_lower:
                    section_boost = 0.05
                elif category == "education" and "education" in sec_lower:
                    section_boost = 0.1

            # 3. Hybrid combined score
            comb_score = (
                settings.RETRIEVAL_VECTOR_WEIGHT * vec_score +
                settings.RETRIEVAL_LEXICAL_WEIGHT * lex_score +
                section_boost
            )

            # Filter out weak/irrelevant noise:
            # Keep if there's an exact lexical match OR combined score passes threshold
            if has_exact or comb_score >= threshold:
                # Find best snippet inside chunk
                snippet = self._extract_best_snippet(chunk.content, matched_keywords, requirement_text)
                candidates.append(RetrievedEvidence(
                    chunk_id=chunk.id,
                    snippet=snippet,
                    section_name=chunk.section_name or "Resume",
                    page_number=chunk.page_number,
                    vector_score=round(vec_score, 4),
                    lexical_score=round(lex_score, 4),
                    combined_score=round(comb_score, 4),
                    has_lexical_match=has_exact
                ))

        # Sort descending by combined score
        candidates.sort(key=lambda x: x.combined_score, reverse=True)
        return candidates[:top_k]

    def _extract_best_snippet(self, chunk_text: str, matched_keywords: List[str], requirement_text: str) -> str:
        """Extracts the most relevant 1-2 sentences containing evidence from the chunk."""
        sentences = [s.strip() for s in re.split(r"[.\n]", chunk_text) if s.strip()]
        if not sentences:
            return chunk_text[:200]

        # Prioritize sentence with matched keywords
        for sentence in sentences:
            s_lower = sentence.lower()
            if any(re.search(rf"\b{re.escape(kw)}\b", s_lower) for kw in matched_keywords):
                return sentence.strip()

        # Fallback to first informative sentence
        return sentences[0][:200]
