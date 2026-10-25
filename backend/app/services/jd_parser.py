import re
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field

@dataclass
class ExtractedRequirement:
    requirement_text: str  # The complete, whole-line requirement statement
    category: str          # programming_language, framework, database, cloud_devops, education, experience, soft_skill, responsibility
    priority: str          # mandatory, preferred
    is_inferred: bool
    context_snippet: str
    lexical_keywords: List[str] = field(default_factory=list)
    confidence: float = 0.95


PREFERRED_PATTERNS = [
    r"(?i)\b(?:preferred|nice to have|plus|bonus|good to have|desired|preferred qualifications|optional|asset)\b"
]

MANDATORY_PATTERNS = [
    r"(?i)\b(?:required|must have|minimum|essential|requirements|qualifications|responsibilities|expected to|what you will do|what you need)\b"
]

BOILERPLATE_PATTERNS = [
    r"(?i)\b(?:equal opportunity|affirmative action|benefits|health insurance|dental|vision|401k|pto|vacation|salary|compensation|perks|commute|hybrid schedule|apply now|about the company|who we are|location:)\b"
]

# Patterns for identifying multi-entity compound lines that should be split into distinct whole-statement requirements
KNOWN_TECH_ENTITIES_WITH_NAMES = [
    ("programming_language", [
        (r"\bpython\b", "Python"),
        (r"\bjava\b", "Java"),
        (r"\bc\+\+\b", "C++"),
        (r"\bc#\b", "C#"),
        (r"\bgolang\b|\bgo\b", "Golang"),
        (r"\brust\b", "Rust"),
        (r"\btypescript\b", "TypeScript"),
        (r"\bjavascript\b", "JavaScript"),
        (r"\bruby\b", "Ruby"),
        (r"\bkotlin\b", "Kotlin"),
        (r"\bswift\b", "Swift"),
        (r"\bscala\b", "Scala"),
        (r"\bphp\b", "PHP"),
        (r"\bsql\b", "SQL"),
    ]),
    ("framework", [
        (r"\breact(?:\.js)?\b", "React"),
        (r"\bnext(?:\.js)?\b", "Next.js"),
        (r"\bvue(?:\.js)?\b", "Vue"),
        (r"\bangular\b", "Angular"),
        (r"\bfastapi\b", "FastAPI"),
        (r"\bspring boot\b", "Spring Boot"),
        (r"\bdjango\b", "Django"),
        (r"\bflask\b", "Flask"),
        (r"\bexpress(?:\.js)?\b", "Express.js"),
        (r"\bnode(?:\.js)?\b", "Node.js"),
        (r"\basp\.net\b", "ASP.NET"),
        (r"\blaravel\b", "Laravel"),
        (r"\btailwind\b", "Tailwind CSS"),
    ]),
    ("database", [
        (r"\bpostgresql\b|\bpostgres\b", "PostgreSQL"),
        (r"\bmysql\b", "MySQL"),
        (r"\bmongodb\b|\bmongo\b", "MongoDB"),
        (r"\bredis\b", "Redis"),
        (r"\bcassandra\b", "Cassandra"),
        (r"\bdynamodb\b", "DynamoDB"),
        (r"\belasticsearch\b", "Elasticsearch"),
        (r"\bsqlite\b", "SQLite"),
        (r"\boracle\b", "Oracle DB"),
    ]),
    ("cloud_devops", [
        (r"\bdocker\b", "Docker"),
        (r"\bkubernetes\b|\bk8s\b", "Kubernetes"),
        (r"\baws\b", "AWS"),
        (r"\bgcp\b|\bgoogle cloud\b", "Google Cloud"),
        (r"\bazure\b", "Azure"),
        (r"\bci/cd\b", "CI/CD"),
        (r"\bgit\b", "Git"),
        (r"\bgithub actions\b", "GitHub Actions"),
        (r"\bjenkins\b", "Jenkins"),
        (r"\bterraform\b", "Terraform"),
        (r"\bansible\b", "Ansible"),
        (r"\blinux\b", "Linux"),
    ])
]

# Patterns for assigning domain categories to full lines
CATEGORY_PATTERNS = [
    (r"(?i)\b(?:degree|bachelor'?s|master'?s|b\.?tech|b\.?e\.?|m\.?tech|phd|diploma|computer science|engineering field)\b", "education"),
    (r"(?i)\b(?:\d+\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)|prior experience|work history|track record)\b", "experience"),
    (r"(?i)\b(?:python|java\b|c\+\+|c#|golang|rust|typescript|javascript|ruby|kotlin|swift|scala|php|sql\b)\b", "programming_language"),
    (r"(?i)\b(?:react|next\.?js|vue|angular|fastapi|spring boot|django|flask|express|node\.?js|asp\.net|laravel|tailwind)\b", "framework"),
    (r"(?i)\b(?:postgresql|postgres|mysql|mongodb|redis|cassandra|dynamodb|elasticsearch|oracle|sqlite|rdbms|nosql)\b", "database"),
    (r"(?i)\b(?:docker|kubernetes|k8s|aws|gcp|azure|ci/cd|git\b|github actions|jenkins|terraform|ansible|linux|devops)\b", "cloud_devops"),
    (r"(?i)\b(?:communication|teamwork|leadership|agile|scrum|problem solving|critical thinking|collaboration|client-facing|stakeholder)\b", "soft_skill"),
]

def clean_requirement_line(line: str) -> str:
    """Removes bullet markers, numbering, and trailing punctuation while preserving the whole statement."""
    cleaned = re.sub(r"^[\s\-*•>#]+", "", line).strip()
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned).strip()
    cleaned = re.sub(r"^[a-zA-Z][\.\)]\s*", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

class JobDescriptionParserService:
    def __init__(self):
        pass

    def parse_job_description(self, raw_text: str) -> List[ExtractedRequirement]:
        """
        Parses raw job description text into complete whole-line requirement statements.
        Preserves the entire sentence meaning, verbs, context, and qualifications instead of isolated words.
        """
        if not raw_text or len(raw_text.strip()) < 20:
            return []

        cleaned_text = raw_text.strip()
        lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

        current_priority = "mandatory"
        extracted: List[ExtractedRequirement] = []
        seen_requirements = set()

        for line in lines:
            line_lower = line.lower()

            # Check if line is a section heading altering default priority
            if any(re.search(p, line_lower) for p in PREFERRED_PATTERNS) and len(line) < 60:
                current_priority = "preferred"
                continue
            elif any(re.search(p, line_lower) for p in MANDATORY_PATTERNS) and "preferred" not in line_lower and len(line) < 60:
                current_priority = "mandatory"
                continue

            # Skip boilerplate administrative statements
            if any(re.search(p, line_lower) for p in BOILERPLATE_PATTERNS) and len(line) > 20:
                continue

            # Skip job metadata lines (e.g. Job Title:, Role:, Company:, Location:)
            if any(line_lower.startswith(p) for p in ["job title:", "title:", "role:", "company:", "location:", "department:"]):
                continue

            # Clean bullet and formatting
            clean_stmt = clean_requirement_line(line)
            is_bullet = line.startswith(("-", "*", "•", ">")) or bool(re.match(r"^\d+[\.\)]", line))
            min_len = 3 if is_bullet else 15

            if len(clean_stmt) < min_len or len(clean_stmt) > 350:
                continue

            # Determine if this line expresses a requirement or responsibility
            has_action_or_qualification = any(
                w in line_lower for w in [
                    "experience", "knowledge", "proficiency", "proficient", "familiarity",
                    "degree", "ability", "responsible", "design", "build", "develop", "lead",
                    "manage", "implement", "create", "collaborate", "ensure", "maintain",
                    "drive", "deploy", "architect", "skills", "understanding", "hands-on", "working with",
                    "qualifications", "requirements", "familiar"
                ]
            )

            # Skip general uninformative introductory sentences if not a bullet
            if not is_bullet and not has_action_or_qualification:
                continue

            # Assign priority for this line
            line_priority = current_priority
            if any(re.search(p, line_lower) for p in PREFERRED_PATTERNS):
                line_priority = "preferred"

            # Check if line contains multiple distinct entity qualifications from DIFFERENT categories
            # e.g., "Proficiency in Python and PostgreSQL" or "Experience with Kubernetes and React"
            entity_matches = []
            for cat, items in KNOWN_TECH_ENTITIES_WITH_NAMES:
                for pat, name in items:
                    m = re.search(pat, line_lower)
                    if m:
                        entity_matches.append((cat, name, m.start()))

            distinct_cats = {m[0] for m in entity_matches}
            is_compound_line = len(distinct_cats) > 1 and (" and " in clean_stmt.lower() or "," in clean_stmt)

            if is_compound_line:
                # Extract prefix like 'Proficiency in' or 'Experience with'
                prefix_match = re.match(
                    r"^(proficiency in|experience with|hands-on experience with|familiarity with|knowledge of|working with)\s+",
                    clean_stmt,
                    re.I
                )
                prefix = prefix_match.group(0).strip() if prefix_match else "Experience with"

                for cat, ent_name, _ in entity_matches:
                    sub_stmt = f"{prefix} {ent_name}"
                    dedup_key = sub_stmt.lower()
                    if dedup_key in seen_requirements:
                        continue
                    seen_requirements.add(dedup_key)

                    words = re.findall(r"\b[A-Za-z0-9+#.-]{3,}\b", sub_stmt.lower())
                    keywords = [w for w in words if w not in {"with", "and", "the", "for", "from", "that", "this", "have", "been", "using", "will", "must", "your", "such"}][:8]

                    extracted.append(ExtractedRequirement(
                        requirement_text=sub_stmt,
                        category=cat,
                        priority=line_priority,
                        is_inferred=False,
                        context_snippet=clean_stmt,
                        lexical_keywords=keywords,
                        confidence=0.95
                    ))
            else:
                # Deduplicate similar statements
                dedup_key = clean_stmt[:50].lower()
                if dedup_key in seen_requirements:
                    continue
                seen_requirements.add(dedup_key)

                # Assign category based on whole line content
                category = "responsibility"
                for cat_pattern, cat_name in CATEGORY_PATTERNS:
                    if re.search(cat_pattern, line_lower):
                        category = cat_name
                        break

                words = re.findall(r"\b[A-Za-z0-9+#.-]{3,}\b", clean_stmt.lower())
                keywords = [w for w in words if w not in {"with", "and", "the", "for", "from", "that", "this", "have", "been", "using", "will", "must", "your", "such"}][:8]

                extracted.append(ExtractedRequirement(
                    requirement_text=clean_stmt,  # THE COMPLETE WHOLE STATEMENT
                    category=category,
                    priority=line_priority,
                    is_inferred=False,
                    context_snippet=clean_stmt,
                    lexical_keywords=keywords,
                    confidence=0.95
                ))

            if len(extracted) >= 20:
                break

        # Fallback if no structured lines were matched (e.g. single block of text)
        if not extracted:
            sentences = [s.strip() for s in re.split(r"[.\n]", cleaned_text) if len(s.strip()) > 20]
            for s in sentences[:8]:
                extracted.append(ExtractedRequirement(
                    requirement_text=s,
                    category="responsibility",
                    priority="mandatory",
                    is_inferred=False,
                    context_snippet=s,
                    lexical_keywords=re.findall(r"\b[A-Za-z]{4,}\b", s.lower())[:6],
                    confidence=0.80
                ))

        return extracted
