import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

@dataclass
class ExtractedRequirement:
    requirement_text: str
    category: str  # programming_language, framework, database, cloud_devops, education, experience, soft_skill, responsibility
    priority: str  # mandatory, preferred
    is_inferred: bool
    context_snippet: str
    lexical_keywords: List[str] = field(default_factory=list)
    confidence: float = 0.95


# Predefined dictionaries for high-precision technical entity extraction
KNOWN_TECH_ENTITIES = {
    "programming_language": [
        "python", "java", "c\\+\\+", "c#", "typescript", "javascript", "golang", "go",
        "rust", "ruby", "kotlin", "swift", "scala", "php", "r", "dart", "sql"
    ],
    "framework": [
        "react", "react\\.js", "next\\.js", "vue", "angular", "fastapi", "spring boot",
        "django", "flask", "express", "express\\.js", "node\\.js", "asp\\.net", "laravel",
        "tailwind", "bootstrap"
    ],
    "database": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "cassandra",
        "dynamodb", "elasticsearch", "sqlite", "oracle", "mariadb"
    ],
    "cloud_devops": [
        "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "ci/cd", "git",
        "github actions", "jenkins", "terraform", "ansible", "linux"
    ],
    "soft_skill": [
        "communication", "teamwork", "leadership", "agile", "scrum", "problem solving",
        "critical thinking", "collaboration"
    ]
}

PREFERRED_PATTERNS = [
    r"(?i)\b(?:preferred|nice to have|plus|bonus|good to have|desired|preferred qualifications|optional)\b"
]

MANDATORY_PATTERNS = [
    r"(?i)\b(?:required|must have|minimum|essential|requirements|qualifications|responsibilities|expected to)\b"
]

class JobDescriptionParserService:
    def __init__(self):
        pass

    def parse_job_description(self, raw_text: str) -> List[ExtractedRequirement]:
        """
        Parses raw job description text into categorized, prioritized, and context-linked requirements.
        """
        if not raw_text or len(raw_text.strip()) < 20:
            return []

        cleaned_text = raw_text.strip()
        lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

        current_priority = "mandatory"
        extracted: List[ExtractedRequirement] = []
        seen_requirements = set()

        # Phase 1: Section-aware line analysis
        for line in lines:
            line_lower = line.lower()
            
            # Check if section header changes default priority
            if any(re.search(p, line_lower) for p in PREFERRED_PATTERNS):
                current_priority = "preferred"
            elif any(re.search(p, line_lower) for p in MANDATORY_PATTERNS) and "preferred" not in line_lower:
                current_priority = "mandatory"

            # Check if line looks like an experience requirement
            exp_match = re.search(r"(\d+\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?[^.\n]*)", line, re.IGNORECASE)
            if exp_match:
                req_text = exp_match.group(1).strip()
                if len(req_text) > 5 and req_text.lower() not in seen_requirements:
                    seen_requirements.add(req_text.lower())
                    extracted.append(ExtractedRequirement(
                        requirement_text=line.strip(" -*•"),
                        category="experience",
                        priority=current_priority,
                        is_inferred=False,
                        context_snippet=line,
                        lexical_keywords=["experience", "years"],
                        confidence=0.95
                    ))
                    continue

            # Check if line is an education requirement
            edu_match = re.search(r"\b(?:bachelor'?s|master'?s|b\.?tech|b\.?e\.?|m\.?tech|phd|degree in (?:computer science|engineering|related field))\b", line_lower)
            if edu_match:
                if "education" not in seen_requirements:
                    seen_requirements.add("education")
                    extracted.append(ExtractedRequirement(
                        requirement_text=line.strip(" -*•"),
                        category="education",
                        priority=current_priority,
                        is_inferred=False,
                        context_snippet=line,
                        lexical_keywords=["degree", "computer science", "bachelor"],
                        confidence=0.95
                    ))
                    continue

            # Check known technical entities in this line
            line_has_entity = False
            for cat, entities in KNOWN_TECH_ENTITIES.items():
                for ent_pattern in entities:
                    pattern = rf"\b{ent_pattern}\b"
                    match = re.search(pattern, line_lower)
                    if match:
                        display_name = ent_pattern.replace("\\", "").title()
                        if display_name.lower() in ["c++", "c#", "ci/cd"]:
                            display_name = ent_pattern.replace("\\", "").upper()
                        elif display_name.lower() in ["react.js", "next.js", "node.js"]:
                            display_name = ent_pattern.replace("\\", "")

                        key = f"{cat}:{display_name.lower()}"
                        if key not in seen_requirements:
                            seen_requirements.add(key)
                            line_has_entity = True
                            
                            # Determine priority for this specific requirement
                            item_priority = current_priority
                            if any(re.search(p, line_lower) for p in PREFERRED_PATTERNS):
                                item_priority = "preferred"

                            extracted.append(ExtractedRequirement(
                                requirement_text=display_name,
                                category=cat,
                                priority=item_priority,
                                is_inferred=False,
                                context_snippet=line.strip(" -*•"),
                                lexical_keywords=[display_name.lower()],
                                confidence=0.98
                            ))

            # If line is a bullet item that looks like a concrete role responsibility
            if not line_has_entity and (line.startswith("-") or line.startswith("*") or line.startswith("•")) and len(line) > 30:
                clean_bullet = line.strip(" -*•")
                bullet_lower = clean_bullet.lower()
                # Exclude purely administrative / company perk sentences
                if not any(k in bullet_lower for k in ["salary", "equity", "health insurance", "401k", "perks", "equal opportunity"]):
                    key = f"responsibility:{clean_bullet[:40].lower()}"
                    if key not in seen_requirements and len(seen_requirements) < 25:
                        seen_requirements.add(key)
                        extracted.append(ExtractedRequirement(
                            requirement_text=clean_bullet,
                            category="responsibility",
                            priority=current_priority,
                            is_inferred=False,
                            context_snippet=clean_bullet,
                            lexical_keywords=re.findall(r"\b[A-Za-z]{4,}\b", clean_bullet)[:5],
                            confidence=0.85
                        ))

        return extracted
