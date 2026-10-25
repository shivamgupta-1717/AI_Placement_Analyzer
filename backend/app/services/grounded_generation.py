import re
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

# Generic functional head words and role nouns across ALL disciplines
# These words describe generic functional activity types or organizational roles, but DO NOT define
# the core substantive domain (e.g. "development" in business development vs software development)
GENERIC_FUNCTIONAL_HEAD_WORDS: Set[str] = {
    "development", "developer", "engineer", "engineering", "manager", "management",
    "lead", "leader", "leadership", "specialist", "consultant", "services", "solutions",
    "operations", "analyst", "analytics", "design", "designer", "testing", "tester",
    "architecture", "architect", "support", "administrator", "administration", "skills",
    "experience", "technologies", "knowledge", "role", "work", "system", "systems",
    "stack", "building", "built", "implemented", "application", "applications", "project",
    "projects", "tool", "tools", "team", "teams", "practice", "practices", "planning",
    "strategy", "process", "processes", "environment", "responsibilities", "responsibility",
    "proficiency", "proficient", "familiarity", "ability", "hands-on", "understanding",
    "working", "overview", "concept", "concepts", "field", "duties", "tasks", "methods",
    "execution", "delivery", "drive", "deliver"
}

STOPWORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "for", "with", "and", "or", "to", "of", "by",
    "from", "as", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do",
    "does", "did", "using", "such", "your", "our", "their", "will", "would", "should",
    "can", "could", "must", "years", "plus", "bonus", "well", "etc", "into", "across",
    "related", "preferred", "required", "good", "strong", "excellent", "proven", "high"
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

def extract_domain_core_tokens(text: str) -> List[str]:
    """
    Extracts the substantive, domain-defining tokens from a requirement or resume statement,
    stripping generic functional head words and grammatical stopwords.
    """
    tokens = re.findall(r"\b[A-Za-z0-9+#.-]{2,}\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS and t not in GENERIC_FUNCTIONAL_HEAD_WORDS]

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
        domain disambiguation across disciplines, and explicit abstention safeguards.
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

        # SAFEGUARD 2: Non-technical context check (e.g., Python as a pet snake in hobbies)
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

        # SAFEGUARD 3: Partial or ambiguous evidence check (webinars, workshops, abandoned projects)
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

        # SAFEGUARD 4: Vague requirement handling (e.g., "modern tech stack")
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

        # SAFEGUARD 5: UNIVERSAL WHOLE-LINE DOMAIN & SEMANTIC CONGRUENCE EVALUATION
        # Extracts substantive domain core tokens (excluding generic functional head words like
        # 'development', 'management', 'analysis', 'design', 'architecture', 'engineer')
        req_core_tokens = extract_domain_core_tokens(requirement_text)

        # Segment retrieved evidence into candidate sentences/statements
        candidate_sentences = [
            s.strip() for ev in retrieved_evidence
            for s in re.split(r"[.\n;]", ev.snippet)
            if len(s.strip()) > 5
        ]

        best_sentence = top_evidence.snippet
        best_domain_overlap: List[str] = []
        best_ratio = 0.0

        for sent in candidate_sentences:
            sent_core = extract_domain_core_tokens(sent)
            matched = [
                t for t in req_core_tokens
                if any(t == sc or (len(t) > 3 and (t in sc or sc in t)) for sc in sent_core)
            ]
            ratio = (len(matched) / len(req_core_tokens)) if req_core_tokens else 1.0
            if ratio > best_ratio:
                best_ratio = ratio
                best_domain_overlap = matched
                best_sentence = sent

        # If the requirement has substantive domain identifiers, evaluate whole-line congruence
        if req_core_tokens:
            # Case A: Complete domain mismatch (0 matching domain tokens)
            # The sentences only matched on generic functional words (e.g., "development", "management", "analysis")
            if best_ratio == 0.0:
                return GroundedSkillResult(
                    requirement_text=requirement_text,
                    category=category,
                    priority=priority,
                    classification="Not found in resume",
                    confidence=0.96,
                    reasoning=(
                        f"The requirement '{requirement_text}' requires specific domain qualifications "
                        f"('{', '.join(req_core_tokens[:4])}'). Although the resume mentions \"{top_evidence.snippet}\" "
                        f"in {top_evidence.section_name}, that experience operates in a distinct functional domain. "
                        f"Evaluated on complete whole-line semantic meaning rather than isolated word overlaps."
                    ),
                    evidence_snippet=top_evidence.snippet,
                    source_section=top_evidence.section_name,
                    page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                    similarity_score=0.10,
                    is_verified_in_source=True
                )

            # Case B: Significant domain gap on multi-token requirements
            if len(req_core_tokens) >= 3 and best_ratio < 0.35:
                return GroundedSkillResult(
                    requirement_text=requirement_text,
                    category=category,
                    priority=priority,
                    classification="Not found in resume",
                    confidence=0.90,
                    reasoning=(
                        f"The resume snippet \"{top_evidence.snippet}\" lacks the primary qualifications "
                        f"('{', '.join(req_core_tokens)}') specified in '{requirement_text}'. "
                        f"Only minor coincidental vocabulary was present."
                    ),
                    evidence_snippet=top_evidence.snippet,
                    source_section=top_evidence.section_name,
                    page_number=str(top_evidence.page_number) if top_evidence.page_number else None,
                    similarity_score=0.20,
                    is_verified_in_source=True
                )

        # If LLM is configured and not in mock mode, invoke grounded LLM evaluation
        if self.llm_service.provider in ["gemini", "openai"]:
            try:
                return self._assess_with_llm(requirement_text, category, priority, retrieved_evidence)
            except Exception:
                pass

        # Deterministic Whole-Sentence Classification
        combined_score = top_evidence.combined_score

        # Check if the domain is verified with high congruence
        if best_ratio >= 0.50 or (not req_core_tokens and combined_score >= 0.70):
            classification = "Demonstrated"
            confidence = min(0.99, max(0.85, round(combined_score, 2)))
            reasoning = (
                f"The resume demonstrates '{requirement_text}' in the {top_evidence.section_name} section: "
                f"\"{best_sentence or top_evidence.snippet}\"."
            )
        elif best_ratio > 0.0 or combined_score >= 0.40:
            classification = "Partially demonstrated"
            confidence = round(combined_score, 2)
            reasoning = (
                f"Related context was retrieved in {top_evidence.section_name} (\"{best_sentence or top_evidence.snippet}\"), "
                f"but comprehensive evidence for the entire requirement '{requirement_text}' is only partially evidenced."
            )
        else:
            classification = "Not found in resume"
            confidence = 0.85
            reasoning = (
                f"The candidate's resume does not substantiate '{requirement_text}'."
            )

        # Citation Grounding Verification
        all_chunk_texts = [e.snippet for e in retrieved_evidence]
        is_verified = verify_citation_grounding(best_sentence or top_evidence.snippet, all_chunk_texts)

        return GroundedSkillResult(
            requirement_text=requirement_text,
            category=category,
            priority=priority,
            classification=classification,
            confidence=confidence,
            reasoning=reasoning,
            evidence_snippet=best_sentence or top_evidence.snippet,
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
        """Calls LLM with strict XML-fenced evidence, whole-line semantic reasoning, and JSON output."""
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
            "You are a rigorous, evidence-based placement resume auditor. Your mission is to evaluate whether a candidate's "
            "resume demonstrates a specific job requirement based EXCLUSIVELY on the provided <evidence> snippets.\n\n"
            "CORE PRINCIPLE: WHOLE-LINE SEMANTIC EVALUATION vs. KEYWORD MATCHING\n"
            "1. Analyze the COMPLETE MEANING, OBJECTIVE, AND DOMAIN of the entire requirement statement against the complete "
            "meaning of the candidate's evidence statements. DO NOT match requirements based on isolated words or tokens.\n"
            "2. Sentences often share common functional words (such as 'development', 'management', 'analysis', 'design', "
            "'architecture', 'engineering', 'operations', 'strategy', 'planning', 'lead', 'system') across entirely different disciplines.\n"
            "   - If a requirement and a resume snippet share words but express completely different domains, activities, or responsibilities, "
            "you MUST classify as 'Not found in resume'.\n"
            "   - For example: Business Development (sales, commercial growth, client acquisition) is entirely DIFFERENT from Software/Web Development (coding, web development). A candidate mentioning Full Stack Development DOES NOT demonstrate Business Development.\n"
            "   - Financial Management is entirely DIFFERENT from State Management in React.\n"
            "   - User Interface Design is entirely DIFFERENT from Database Design or Network Architecture Design.\n"
            "3. Allowed classifications: 'Demonstrated', 'Partially demonstrated', 'Not found in resume', 'Uncertain'.\n"
            "4. Respond with valid JSON matching this schema:\n"
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
