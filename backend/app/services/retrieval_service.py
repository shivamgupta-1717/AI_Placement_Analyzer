import re
from typing import List, Optional, Set
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


from app.services.grounded_generation import GENERIC_FUNCTIONAL_HEAD_WORDS as GENERIC_HEAD_WORDS

STOPWORDS: Set[str] = {
    "and", "the", "for", "with", "must", "have", "preferred", "years", "degree",
    "from", "that", "this", "been", "using", "able", "such", "well", "plus", "bonus",
    "about", "into", "over", "after", "before", "between", "under", "above"
}

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
        (vector cosine + whole-phrase/distinctive-modifier lexical) search,
        with semantic disambiguation and relevance threshold filtering.
        """
        chunks = self.db.query(ResumeChunk).filter(ResumeChunk.resume_id == resume_id).all()
        if not chunks:
            return []

        # Generate query embedding for requirement
        query_vec = self.embedding_service.get_embedding(requirement_text)

        # Clean normalized requirement phrase
        clean_req_phrase = requirement_text.lower().strip()

        # Extract all tokens from requirement
        raw_tokens = re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", clean_req_phrase)
        content_tokens = [t for t in raw_tokens if t not in STOPWORDS]

        # Extract DISTINCTIVE non-generic tokens (the critical modifiers, e.g. "business" in "business development")
        distinctive_tokens = [t for t in content_tokens if t not in GENERIC_HEAD_WORDS]
        # If all tokens were in generic head words (e.g. single word "Architecture"), keep them
        if not distinctive_tokens and content_tokens:
            distinctive_tokens = content_tokens

        candidates: List[RetrievedEvidence] = []

        for chunk in chunks:
            # 1. Vector similarity
            chunk_vec = chunk.embedding
            vec_score = 0.0
            if chunk_vec:
                vec_score = self.embedding_service.cosine_similarity(query_vec, chunk_vec)
                vec_score = max(0.0, min(1.0, (vec_score + 1.0) / 2.0))

            # 2. Precise Whole-Phrase & Distinctive Lexical Match Check
            chunk_lower = chunk.content.lower()

            # Check A: Exact continuous phrase match (e.g. "business development" in chunk)
            exact_phrase_match = bool(re.search(rf"\b{re.escape(clean_req_phrase)}\b", chunk_lower))

            # Check B: Distinctive modifiers match
            # To prevent "business development" from matching "full stack development",
            # ALL distinctive modifiers of the requirement MUST be present in the chunk!
            matched_distinctive = [t for t in distinctive_tokens if re.search(rf"\b{re.escape(t)}\b", chunk_lower)]
            all_distinctive_matched = len(distinctive_tokens) > 0 and (len(matched_distinctive) == len(distinctive_tokens))

            # Partial distinctive match ratio
            distinctive_ratio = (len(matched_distinctive) / len(distinctive_tokens)) if distinctive_tokens else 0.0

            has_exact = False
            lex_score = 0.0

            if exact_phrase_match:
                has_exact = True
                lex_score = 1.0
            elif all_distinctive_matched:
                has_exact = True
                lex_score = 0.9
            elif distinctive_ratio >= 0.5 and len(distinctive_tokens) > 1:
                # E.g. 2 out of 3 distinctive words matched
                lex_score = 0.5
            else:
                # Merely matching generic words like "development" or "engineer" gives 0.0 lexical score
                lex_score = 0.0
                has_exact = False

            # Section boost (e.g. programming_language in Skills section)
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
            # Keep if there's an authentic lexical match OR combined score passes threshold
            if has_exact or comb_score >= threshold:
                snippet = self._extract_best_snippet(chunk.content, matched_distinctive, clean_req_phrase)
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

        candidates.sort(key=lambda x: x.combined_score, reverse=True)
        return candidates[:top_k]

    def _extract_best_snippet(self, chunk_text: str, matched_keywords: List[str], requirement_phrase: str) -> str:
        """Extracts the most relevant 1-2 sentences containing evidence from the chunk."""
        sentences = [s.strip() for s in re.split(r"[.\n]", chunk_text) if s.strip()]
        if not sentences:
            return chunk_text[:200]

        # Prioritize exact phrase
        for sentence in sentences:
            if re.search(rf"\b{re.escape(requirement_phrase)}\b", sentence.lower()):
                return sentence.strip()

        # Prioritize sentence with matched distinctive keywords
        if matched_keywords:
            for sentence in sentences:
                s_lower = sentence.lower()
                if all(re.search(rf"\b{re.escape(kw)}\b", s_lower) for kw in matched_keywords):
                    return sentence.strip()

            for sentence in sentences:
                s_lower = sentence.lower()
                if any(re.search(rf"\b{re.escape(kw)}\b", s_lower) for kw in matched_keywords):
                    return sentence.strip()

        return sentences[0][:200]
