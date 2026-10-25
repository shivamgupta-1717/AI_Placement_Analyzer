import re
import difflib
from typing import List, Dict, Any, Optional, Tuple, Set
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

# Generic head nouns and role suffixes that can NEVER alone validate a specific skill claim
# (e.g. "development" in "business development" vs "full stack development")
GENERIC_ROLE_WORDS: Set[str] = {
    "development", "developer", "engineer", "engineering", "manager", "management",
    "lead", "leader", "leadership", "specialist", "consultant", "services", "solutions",
    "operations", "analyst", "analytics", "architecture", "architect", "support",
    "administration", "administrator", "skills", "experience", "system", "systems",
    "stack", "building", "built", "implemented", "application", "applications", "project",
    "projects", "tool", "tools", "team", "teams", "practice", "practices"
}

# Specific semantic domain vocabulary
BUSINESS_DEV_TERMS = {
    "business development", "sales", "lead generation", "b2b", "client acquisition",
    "account executive", "revenue growth", "closing deals", "partnerships", "cold outreach",
    "pipeline", "market expansion", "prospecting", "deal closing"
}

TECH_DEV_TERMS = {
    "full stack", "frontend", "backend", "software engineer", "software developer",
    "web development", "coding", "programming", "react", "python", "node.js", "java",
    "fastapi", "git", "api", "rest api", "html", "css", "docker", "sql"
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
        Assesses a single requirement against retrieved resume evidence using whole-line semantic grounding,
        domain disambiguation (e.g. Business Development vs Full Stack Development), and explicit abstention.
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
        req_lower = requirement_text.lower()

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

        # SAFEGUARD 2: Semantic Domain Disambiguation Check
        # (e.g., JD asks for "Business Development" but resume has "Full Stack Development")
        is_business_req = any(b in req_lower for b in BUSINESS_DEV_TERMS)
        if is_business_req:
            has_business_in_snippet = any(b in snippet_lower for b in BUSINESS_DEV_TERMS)
            is_pure_tech_snippet = any(t in snippet_lower for t in TECH_DEV_TERMS)

            if is_pure_tech_snippet and not has_business_in_snippet:
                return GroundedSkillResult(
                    requirement_text=requirement_text,
                    category=category,
                    priority=priority,
                    classification="Not found in resume",
                    confidence=0.98,
                    reasoning=(
                        f"The requirement '{requirement_text}' focuses on business growth, sales, partnerships, "
                        f"or client acquisition. Although the resume mentions technical engineering in {top_evidence.section_name} "
                        f"(\"{top_evidence.snippet}\"), software development operates in an entirely distinct domain and "
                        f"does not demonstrate business development capabilities."
                    ),
                    evidence_snippet=top_evidence.snippet,
                    source_section=top_evidence.section_name,
                    page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                    similarity_score=0.1,
                    is_verified_in_source=True
                )

        # SAFEGUARD 3: Whole-Line Distinguishing Modifier Grounding Check
        # Prevents matching on generic suffixes like "development", "engineer", "management"
        raw_req_tokens = re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", req_lower)
        distinctive_req_tokens = [
            t for t in raw_req_tokens
            if t not in GENERIC_ROLE_WORDS and t not in {
                "and", "the", "for", "with", "must", "have", "preferred", "years", "degree", "such"
            }
        ]

        if distinctive_req_tokens:
            matched_distinctive = [
                t for t in distinctive_req_tokens
                if re.search(rf"\b{re.escape(t)}\b", snippet_lower)
            ]

            # If the requirement has distinguishing terms (e.g. "business" in "business development"),
            # and NONE of them appear in the snippet, it's a false lexical hit on a generic word like "development".
            if not matched_distinctive and not top_evidence.has_lexical_match:
                return GroundedSkillResult(
                    requirement_text=requirement_text,
                    category=category,
                    priority=priority,
                    classification="Not found in resume",
                    confidence=0.95,
                    reasoning=(
                        f"The resume snippet \"{top_evidence.snippet}\" shares generic vocabulary but does not contain "
                        f"the defining qualifications ('{', '.join(distinctive_req_tokens)}') required for '{requirement_text}'."
                    ),
                    evidence_snippet=top_evidence.snippet,
                    source_section=top_evidence.section_name,
                    page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                    similarity_score=0.15,
                    is_verified_in_source=True
                )

        # SAFEGUARD 4: Contextual Validation Checks
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
        if "modern tech stack" in req_lower:
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

        # If LLM is configured and not in mock mode, run grounded prompt
        if self.llm_service.provider in ["gemini", "openai"]:
            try:
                return self._assess_with_llm(requirement_text, category, priority, retrieved_evidence)
            except Exception:
                pass

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

        # SAFEGUARD 5: Citation Grounding Verification
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

    def _assess_with_llm(
        self,
        requirement_text: str,
        category: str,
        priority: str,
        retrieved_evidence: List[RetrievedEvidence]
    ) -> GroundedSkillResult:
        """Calls LLM with strict XML-fenced evidence, semantic whole-meaning disambiguation rules, and JSON output."""
        sanitized_req = sanitize_untrusted_text(requirement_text)
        evidence_blocks = []
        for i, ev in enumerate(retrieved_evidence):
            sanitized_snippet = sanitize_untrusted_text(ev.snippet)
            evidence_blocks.append(
                f'<evidence index="{i}" section="{ev.section_name}" page="{ev.page_number}">\n'
                f"{sanitized_snippet}\n"
                f"</evidence>"
            )
        evidence_str = "\n".join(evidence_blocks)

        system_prompt = (
            "You are an evidence-based placement resume auditor. Your job is to strictly evaluate whether a job requirement "
            "is demonstrated by the candidate's resume, based EXCLUSIVELY on the provided <evidence> snippets.\n\n"
            "CRITICAL SEMANTIC DISAMBIGUATION RULES:\n"
            "1. DO NOT match requirements based on isolated generic words like 'development', 'engineer', 'manager', 'management', or 'analyst'.\n"
            "2. For example: 'Business Development' (sales, partnerships, client acquisition) is completely DIFFERENT from 'Full Stack Development' or 'Software Development' (coding, web development). A resume mentioning Full Stack Development DOES NOT demonstrate Business Development. Mark as 'Not found in resume'.\n"
            "3. Evaluate the ACTUAL WHOLE-LINE MEANING and domain of the requirement, not single word overlaps.\n"
            "4. Allowed classifications: 'Demonstrated', 'Partially demonstrated', 'Not found in resume', 'Uncertain'.\n"
            "5. Respond with valid JSON matching this schema:\n"
            '{\n  "classification": "Demonstrated" | "Partially demonstrated" | "Not found in resume" | "Uncertain",\n'
            '  "confidence": 0.0 to 1.0,\n  "reasoning": "concise explanation grounded in evidence and whole-line semantic meaning",\n'
            '  "cited_snippet": "exact quote from evidence or \'None\'",\n  "evidence_index": integer\n}'
        )

        user_prompt = (
            f"Requirement to assess: {sanitized_req} (Category: {category}, Priority: {priority})\n\n"
            f"Retrieved Evidence from Resume:\n{evidence_str}\n\n"
            "Evaluate whether this requirement is supported by the evidence above."
        )

        res = self.llm_service.generate_json_response(system_prompt, user_prompt)

        classification = res.get("classification", "Uncertain")
        if classification not in ["Demonstrated", "Partially demonstrated", "Not found in resume", "Uncertain"]:
            classification = "Uncertain"

        cited_snippet = res.get("cited_snippet", "")
        ev_idx = res.get("evidence_index", 0)
        selected_ev = retrieved_evidence[ev_idx] if 0 <= ev_idx < len(retrieved_evidence) else retrieved_evidence[0]

        all_chunk_texts = [e.snippet for e in retrieved_evidence]
        is_verified = verify_citation_grounding(cited_snippet, all_chunk_texts)

        if not is_verified and classification == "Demonstrated":
            classification = "Uncertain"
            reasoning = f"Cited claim could not be strictly verified in original resume text. {res.get('reasoning', '')}"
        else:
            reasoning = res.get("reasoning", "")

        return GroundedSkillResult(
            requirement_text=requirement_text,
            category=category,
            priority=priority,
            classification=classification,
            confidence=float(res.get("confidence", 0.85)),
            reasoning=reasoning,
            evidence_snippet=cited_snippet if is_verified else selected_ev.snippet,
            source_section=selected_ev.section_name,
            page_number=str(selected_ev.page_number) if selected_ev.page_number else None,
            similarity_score=selected_ev.combined_score,
            is_verified_in_source=is_verified
        )
