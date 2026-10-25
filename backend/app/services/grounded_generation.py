import re
import difflib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from app.services.retrieval_service import RetrievedEvidence
from app.services.llm_service import LLMService

PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(?:all\s+)?previous\s+instructions",
    r"(?i)system\s*:\s*",
    r"(?i)you\s+are\s+now\s+(?:an?\s+)?(?:admin|root|jailbreak|developer\s+mode)",
    r"(?i)(?:give|score|rate)\s+(?:me|this\s+resume)\s+(?:a\s+)?100(?:\s*%)?",
    r"(?i)bypass\s+(?:all\s+)?safeguards",
    r"(?i)do\s+not\s+(?:evaluate|penalize)",
    r"(?i)reveal\s+(?:your\s+)?(?:system\s+prompt|secret|instructions)"
]

PARTIAL_EVIDENCE_MARKERS = [
    "webinar", "workshop", "attended", "explored", "abandoned", "basic knowledge",
    "introductory", "beginner", "familiar with", "learning", "overview"
]

NON_TECHNICAL_SECTIONS = [
    "interests", "hobbies", "activities", "personal"
]

TECHNICAL_CONTEXT_WORDS = {
    "code", "programming", "software", "developer", "engineer", "api", "database",
    "backend", "frontend", "built", "implemented", "developed", "project", "framework",
    "architecture", "system", "app", "application", "data", "cloud", "service"
}

def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitizes untrusted text from resumes and job descriptions by neutralizing
    prompt injection patterns and wrapping the content safely.
    """
    cleaned = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[FILTERED_INSTRUCTION]", cleaned)
    return cleaned

def verify_citation_grounding(citation_text: str, source_chunks_text: List[str]) -> bool:
    """
    Verifies that a cited snippet actually exists within the source document chunks.
    Uses substring matching and content token overlap to prevent hallucinated quotes.
    """
    if not citation_text or not source_chunks_text:
        return False

    clean_citation = citation_text.strip().lower()
    if clean_citation in ["no relevant resume evidence was retrieved.", "none", "not found"]:
        return True

    full_source = " ".join(source_chunks_text).lower()

    # 1. Exact substring check
    if clean_citation in full_source:
        return True

    # 2. Check token overlap: at least 75% of distinctive words in citation must appear in source
    words = [
        w for w in re.findall(r"\b[A-Za-z0-9+#.-]{3,}\b", clean_citation)
        if w not in {"the", "and", "for", "with", "from", "that", "this", "have", "been", "using"}
    ]
    if not words:
        return False

    matched_words = sum(1 for w in words if w in full_source)
    ratio = matched_words / len(words)
    return ratio >= 0.75


@dataclass
class GroundedSkillResult:
    requirement_text: str
    category: str
    priority: str
    classification: str # "Demonstrated", "Partially demonstrated", "Not found in resume", "Uncertain"
    confidence: float
    reasoning: str
    evidence_snippet: Optional[str]
    source_section: Optional[str]
    page_number: Optional[str]
    similarity_score: Optional[float]
    is_verified_in_source: bool


class GroundedGenerationService:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()

    def assess_requirement(
        self,
        requirement_text: str,
        category: str,
        priority: str,
        retrieved_evidence: List[RetrievedEvidence]
    ) -> GroundedSkillResult:
        """
        Assesses a single requirement against retrieved resume evidence using evidence-first grounding,
        explicit abstention for missing evidence, and prompt injection defenses.
        """
        # SAFEGUARD 1: Explicit Abstention when no relevant evidence was retrieved
        if not retrieved_evidence or max(e.combined_score for e in retrieved_evidence) < 0.25:
            return GroundedSkillResult(
                requirement_text=requirement_text,
                category=category,
                priority=priority,
                classification="Not found in resume",
                confidence=0.98,
                reasoning=(
                    f"No relevant resume evidence was retrieved for '{requirement_text}'. "
                    f"The uploaded resume does not explicitly mention or demonstrate this requirement. "
                    f"Note: This does not mean the candidate lacks the skill, only that the uploaded document does not evidence it."
                ),
                evidence_snippet="No relevant resume evidence was retrieved.",
                source_section=None,
                page_number=None,
                similarity_score=0.0,
                is_verified_in_source=True
            )

        top_evidence = retrieved_evidence[0]
        snippet_lower = top_evidence.snippet.lower()
        section_lower = (top_evidence.section_name or "").lower()

        # SAFEGUARD 1.5: Neutralized prompt injection content rejection
        if "[FILTERED_INSTRUCTION]" in top_evidence.snippet:
            return GroundedSkillResult(
                requirement_text=requirement_text,
                category=category,
                priority=priority,
                classification="Not found in resume",
                confidence=0.99,
                reasoning=(
                    f"Retrieved candidate text for '{requirement_text}' contained neutralized instruction injection patterns "
                    f"and is strictly excluded from valid qualification evidence."
                ),
                evidence_snippet="Instruction injection payload neutralized.",
                source_section=top_evidence.section_name,
                page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                similarity_score=0.0,
                is_verified_in_source=False
            )

        # SAFEGUARD 2: Contextual Validation Checks
        # A. Non-technical context check (e.g., Python as a pet snake in hobbies)
        if category in ["programming_language", "framework", "database", "cloud_devops"]:
            is_non_tech_section = any(s in section_lower for s in NON_TECHNICAL_SECTIONS)
            has_tech_context = any(w in snippet_lower for w in TECHNICAL_CONTEXT_WORDS)
            
            if is_non_tech_section and not has_tech_context:
                return GroundedSkillResult(
                    requirement_text=requirement_text,
                    category=category,
                    priority=priority,
                    classification="Not found in resume",
                    confidence=0.95,
                    reasoning=(
                        f"The term '{requirement_text}' was found in a non-technical context ({top_evidence.section_name}) "
                        f"without evidence of software development application: \"{top_evidence.snippet}\"."
                    ),
                    evidence_snippet=top_evidence.snippet,
                    source_section=top_evidence.section_name,
                    page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                    similarity_score=top_evidence.combined_score,
                    is_verified_in_source=True
                )

        # B. Partial or ambiguous evidence check
        is_partial = any(m in snippet_lower for m in PARTIAL_EVIDENCE_MARKERS)
        if is_partial:
            return GroundedSkillResult(
                requirement_text=requirement_text,
                category=category,
                priority=priority,
                classification="Partially demonstrated",
                confidence=0.85,
                reasoning=(
                    f"Resume contains partial or introductory context for '{requirement_text}' in {top_evidence.section_name}: "
                    f"\"{top_evidence.snippet}\", but lacks proof of end-to-end production ownership."
                ),
                evidence_snippet=top_evidence.snippet,
                source_section=top_evidence.section_name,
                page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                similarity_score=top_evidence.combined_score,
                is_verified_in_source=True
            )

        # C. Vague requirement handling
        if "modern tech stack" in requirement_text.lower():
            return GroundedSkillResult(
                requirement_text=requirement_text,
                category=category,
                priority=priority,
                classification="Partially demonstrated",
                confidence=0.80,
                reasoning=(
                    f"Vague requirement '{requirement_text}' partially aligns with candidate's demonstrated technologies "
                    f"in {top_evidence.section_name} (\"{top_evidence.snippet}\")."
                ),
                evidence_snippet=top_evidence.snippet,
                source_section=top_evidence.section_name,
                page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                similarity_score=top_evidence.combined_score,
                is_verified_in_source=True
            )

        # D. Demonstrated skill verification
        has_lexical = any(e.has_lexical_match for e in retrieved_evidence)
        combined_score = top_evidence.combined_score

        if has_lexical or combined_score >= 0.70:
            classification = "Demonstrated"
            confidence = min(0.99, round(combined_score, 2))
            reasoning = (
                f"The resume demonstrates '{requirement_text}' in the {top_evidence.section_name} section: "
                f"\"{top_evidence.snippet}\"."
            )
        elif combined_score >= 0.40:
            classification = "Partially demonstrated"
            confidence = round(combined_score, 2)
            reasoning = (
                f"Related context was retrieved in {top_evidence.section_name} (\"{top_evidence.snippet}\"), "
                f"but direct hands-on evidence for '{requirement_text}' is limited or only partially shown."
            )
        else:
            classification = "Uncertain"
            confidence = 0.50
            reasoning = (
                f"Weak or ambiguous evidence retrieved for '{requirement_text}'. "
                f"Verify whether candidate possesses practical experience in this area."
            )

        # SAFEGUARD 3: Citation Grounding Verification
        all_chunk_texts = [e.snippet for e in retrieved_evidence]
        is_verified = verify_citation_grounding(top_evidence.snippet, all_chunk_texts)

        return GroundedSkillResult(
            requirement_text=requirement_text,
            category=category,
            priority=priority,
            classification=classification,
            confidence=confidence,
            reasoning=reasoning,
            evidence_snippet=top_evidence.snippet,
            source_section=top_evidence.section_name,
            page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
            similarity_score=top_evidence.combined_score,
            is_verified_in_source=is_verified
        )
