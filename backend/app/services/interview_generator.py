import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class GeneratedInterviewQuestion:
    question: str
    category: str # "core_technical", "coding_problem", "project_deep_dive", "scenario_based", "behavioral"
    difficulty: str # "easy", "medium", "hard"
    relevance_rationale: str
    source_type: str # "job_requirement", "resume_project", "role_knowledge"
    key_concepts: List[str]
    answer_guidance: Optional[str]


class InterviewQuestionGeneratorService:
    def __init__(self):
        pass

    def generate_questions(
        self,
        skill_assessments: List[Dict[str, Any]],
        resume_text: str,
        job_title: Optional[str] = "Software Engineer",
        difficulty_filter: Optional[str] = "mixed"
    ) -> List[GeneratedInterviewQuestion]:
        """
        Generates role-specific, evidence-grounded interview questions based on
        job requirements and verified resume projects.
        """
        questions: List[GeneratedInterviewQuestion] = []
        target_role = job_title or "Software Engineer"

        # 1. Project Deep Dive (Grounded in Candidate's Actual Resume)
        project_snippets = self._extract_project_snippets(resume_text)
        for proj_title, proj_snippet in project_snippets[:2]:
            questions.append(GeneratedInterviewQuestion(
                question=(
                    f"In your project '{proj_title}', you mentioned: \"{proj_snippet}\". "
                    f"What was the most challenging technical bottleneck you encountered, and how did you diagnose and resolve it?"
                ),
                category="project_deep_dive",
                difficulty="medium" if difficulty_filter in ["mixed", "medium"] else difficulty_filter,
                relevance_rationale=(
                    f"Directly assesses technical ownership and implementation depth on a project "
                    f"verifiable from your uploaded resume."
                ),
                source_type="resume_project",
                key_concepts=["Architecture decisions", "Root cause analysis", "Trade-offs", "Debugging"],
                answer_guidance=(
                    "Structure your response using the STAR method (Situation, Task, Action, Result). "
                    "Quantify performance improvements or uptime impact if possible."
                )
            ))

        # 2. Technology Requirements Questions (from demonstrated skills)
        demonstrated_skills = [a for a in skill_assessments if a.get("classification") == "Demonstrated"]
        for skill_item in demonstrated_skills[:2]:
            skill_name = skill_item.get("requirement_text")
            q_obj = self._build_technical_question(skill_name, target_role, "medium")
            if q_obj:
                questions.append(q_obj)

        # 3. Gap & Scenario-Based Questions (from missing or partial requirements)
        gap_skills = [
            a for a in skill_assessments
            if a.get("classification") in ["Partially demonstrated", "Not found in resume"]
            and a.get("priority") == "mandatory"
        ]
        for gap_item in gap_skills[:2]:
            gap_name = gap_item.get("requirement_text")
            questions.append(GeneratedInterviewQuestion(
                question=(
                    f"The role of {target_role} emphasizes '{gap_name}'. "
                    f"How would you approach designing a scalable solution using or integrating with {gap_name}, "
                    f"and what best practices would you prioritize?"
                ),
                category="scenario_based",
                difficulty="hard" if difficulty_filter in ["mixed", "hard"] else difficulty_filter,
                relevance_rationale=(
                    f"Prepares you for questions on mandatory job requirements where your resume "
                    f"does not currently show extensive evidence."
                ),
                source_type="job_requirement",
                key_concepts=[gap_name, "System Design", "Scalability", "Fault tolerance"],
                answer_guidance=(
                    f"Acknowledge your foundational understanding of {gap_name}, highlight analogous concepts "
                    f"from related tools you already master, and walk through architectural considerations step by step."
                )
            ))

        # 4. Coding & Problem Solving Question
        questions.append(GeneratedInterviewQuestion(
            question=(
                f"Given a high-throughput stream of events in a {target_role} service, "
                "how would you design an algorithm to find the top-K most frequent items in real time with bounded memory?"
            ),
            category="coding_problem",
            difficulty="medium",
            relevance_rationale=f"Core algorithmic problem solving frequently evaluated in technical placement rounds.",
            source_type="role_knowledge",
            key_concepts=["Min-heap / Priority Queue", "Hash Map", "Count-Min Sketch", "Time & Space Complexity"],
            answer_guidance="Discuss the naive Hash Map + Sort O(N log N) approach, then optimize to O(N log K) using a Min-Heap."
        ))

        # 5. Behavioral / Collaboration Question
        questions.append(GeneratedInterviewQuestion(
            question=(
                "Describe a situation where you had a disagreement with a team member or stakeholder "
                "regarding an architectural choice or project deadline. How did you handle the discussion and what was the outcome?"
            ),
            category="behavioral",
            difficulty="easy",
            relevance_rationale="Assesses engineering communication, empathy, and constructive collaboration in cross-functional teams.",
            source_type="role_knowledge",
            key_concepts=["Active listening", "Data-driven negotiation", "Constructive compromise", "Team success"],
            answer_guidance="Focus on separating ideas from ego, using benchmark data or proof-of-concepts, and committing fully to the decided direction."
        ))

        # Filter by requested difficulty if specific
        if difficulty_filter in ["easy", "medium", "hard"]:
            for q in questions:
                q.difficulty = difficulty_filter

        return questions

    def _extract_project_snippets(self, resume_text: str) -> List[tuple]:
        """Extracts 1-2 real project phrases from resume text without hallucination."""
        snippets = []
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        
        in_project_section = False
        current_title = "Candidate Project"

        for line in lines:
            line_clean = line.strip(" -*#•")
            line_lower = line_clean.lower()

            if any(h in line_lower for h in ["projects", "academic projects", "key projects"]):
                in_project_section = True
                continue
            elif in_project_section and any(h in line_lower for h in ["education", "experience", "certifications", "skills"]):
                in_project_section = False

            if in_project_section:
                # Check if line looks like a project title
                if len(line_clean) < 50 and not line_clean.endswith(".") and not line_clean.startswith("-"):
                    current_title = line_clean
                elif len(line_clean) > 30:
                    snippets.append((current_title, line_clean[:120]))
                    if len(snippets) >= 2:
                        break

        # Fallback if no explicit project section header detected
        if not snippets:
            for line in lines:
                if any(w in line.lower() for w in ["developed", "built", "implemented", "designed"]) and len(line) > 35:
                    snippets.append(("Applied Engineering Project", line.strip(" -*•")[:120]))
                    if len(snippets) >= 2:
                        break

        return snippets

    def _build_technical_question(self, skill_name: str, role: str, difficulty: str) -> Optional[GeneratedInterviewQuestion]:
        skill_lower = skill_name.lower()

        if "python" in skill_lower:
            return GeneratedInterviewQuestion(
                question="How does Python's Global Interpreter Lock (GIL) impact multithreaded CPU-bound tasks versus I/O-bound tasks, and how would you bypass it for concurrent computation?",
                category="core_technical",
                difficulty=difficulty,
                relevance_rationale="Evaluates in-depth runtime knowledge of Python as evidenced on your resume.",
                source_type="job_requirement",
                key_concepts=["GIL", "Multiprocessing vs Threading", "Asyncio", "C extensions"],
                answer_guidance="Explain that GIL prevents simultaneous bytecode execution across threads; recommend `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for CPU-bound tasks."
            )
        elif "react" in skill_lower:
            return GeneratedInterviewQuestion(
                question="Explain the React Fiber reconciliation algorithm and how React handles state batching and side effects in concurrent mode.",
                category="core_technical",
                difficulty=difficulty,
                relevance_rationale="Validates your practical understanding of React's internal rendering pipeline.",
                source_type="job_requirement",
                key_concepts=["Virtual DOM", "Fiber Tree", "Batching", "useTransition / Suspense"],
                answer_guidance="Discuss incremental rendering, priority-based updates, and how React 18 automatic batching reduces redundant re-renders."
            )
        elif "sql" in skill_lower or "postgres" in skill_lower:
            return GeneratedInterviewQuestion(
                question="What is the difference between optimistic and pessimistic locking in database transactions, and in what scenario would each be preferred?",
                category="core_technical",
                difficulty=difficulty,
                relevance_rationale="Tests transactional integrity and database concurrency control.",
                source_type="job_requirement",
                key_concepts=["ACID", "SELECT FOR UPDATE", "Versioning / Timestamping", "Deadlocks"],
                answer_guidance="Optimistic locking assumes conflict is rare (version checking on commit); pessimistic locks records upfront. Use optimistic for high-read e-commerce carts."
            )
        else:
            return GeneratedInterviewQuestion(
                question=f"Can you explain the core architectural principles of {skill_name} and describe a real-world scenario where you had to debug an unexpected behavior?",
                category="core_technical",
                difficulty=difficulty,
                relevance_rationale=f"Evaluates depth of experience in {skill_name}, which is required for the {role} position.",
                source_type="job_requirement",
                key_concepts=[skill_name, "Architecture", "Debugging", "Best Practices"],
                answer_guidance=f"Describe design trade-offs, configuration pitfalls, and telemetry/logging tools you used when working with {skill_name}."
            )
