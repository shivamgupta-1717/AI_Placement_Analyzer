import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.resume import Resume, ResumeChunk
from app.models.job_description import JobDescription, JobRequirement
from app.models.analysis import Analysis, SkillAssessment, EvidenceCitation, LearningItem, InterviewQuestion
from app.services.jd_parser import JobDescriptionParserService, ExtractedRequirement
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.grounded_generation import GroundedGenerationService
from app.services.roadmap_generator import RoadmapGeneratorService
from app.services.interview_generator import InterviewQuestionGeneratorService
from app.core.scoring import calculate_transparent_match_score

logger = logging.getLogger(__name__)

class ResumeAnalyzerOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.jd_parser = JobDescriptionParserService()
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService(db=self.db, embedding_service=self.embedding_service)
        self.grounded_generator = GroundedGenerationService()
        self.roadmap_generator = RoadmapGeneratorService()
        self.interview_generator = InterviewQuestionGeneratorService()

    def run_analysis(
        self,
        resume_id: str,
        job_description_raw: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        experience_level: Optional[str] = None
    ) -> Analysis:
        """
        Orchestrates the entire end-to-end RAG analysis pipeline:
        Ingestion -> Parsing -> Embeddings -> Hybrid Retrieval -> Evidence Verification -> Scoring -> Roadmap -> Questions.
        """
        # Step 1: Verify resume exists
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume with ID '{resume_id}' not found.")

        # Step 2: Create JobDescription record
        effective_title = job_title or "Target Software Role"
        jd = JobDescription(
            title=effective_title,
            company=company_name or "Target Company",
            experience_level=experience_level or "Entry to Mid Level",
            raw_text=job_description_raw
        )
        self.db.add(jd)
        self.db.flush()

        # Step 3: Parse Job Description into structured requirements
        extracted_reqs: List[ExtractedRequirement] = self.jd_parser.parse_job_description(job_description_raw)
        if not extracted_reqs:
            # Fallback for short or unstructured JD
            extracted_reqs = [
                ExtractedRequirement(
                    requirement_text="General Software Engineering & Problem Solving",
                    category="soft_skill",
                    priority="mandatory",
                    is_inferred=True,
                    context_snippet=job_description_raw[:150],
                    lexical_keywords=["software", "engineering", "problem"],
                    confidence=0.7
                )
            ]

        # Save JobRequirements and generate their embeddings
        req_models: List[JobRequirement] = []
        for req in extracted_reqs:
            req_vec = self.embedding_service.get_embedding(req.requirement_text)
            jr = JobRequirement(
                job_description_id=jd.id,
                requirement_text=req.requirement_text,
                category=req.category,
                priority=req.priority,
                is_inferred=req.is_inferred,
                context_snippet=req.context_snippet,
                lexical_keywords=req.lexical_keywords,
                embedding=req_vec
            )
            self.db.add(jr)
            req_models.append(jr)
        self.db.flush()

        # Step 4: Hybrid Evidence Retrieval & Grounded Generation for each requirement
        skill_assessment_records: List[SkillAssessment] = []
        assessment_dicts_for_scoring: List[Dict[str, Any]] = []

        # Create base Analysis record
        analysis = Analysis(
            resume_id=resume.id,
            job_description_id=jd.id,
            status="processing"
        )
        self.db.add(analysis)
        self.db.flush()

        limitations_disclosures = []

        for jr in req_models:
            # Retrieve evidence using hybrid search
            evidence_list = self.retrieval_service.retrieve_evidence_for_requirement(
                resume_id=resume.id,
                requirement_text=jr.requirement_text,
                lexical_keywords=jr.lexical_keywords,
                category=jr.category
            )

            # Grounded generation with citation verification and abstention safeguards
            grounded_res = self.grounded_generator.assess_requirement(
                requirement_text=jr.requirement_text,
                category=jr.category,
                priority=jr.priority,
                retrieved_evidence=evidence_list
            )

            assessment_dicts_for_scoring.append({
                "requirement_text": grounded_res.requirement_text,
                "priority": grounded_res.priority,
                "classification": grounded_res.classification
            })

            # Record SkillAssessment
            sa = SkillAssessment(
                analysis_id=analysis.id,
                requirement_id=jr.id,
                requirement_text=grounded_res.requirement_text,
                category=grounded_res.category,
                priority=grounded_res.priority,
                classification=grounded_res.classification,
                confidence=grounded_res.confidence,
                reasoning=grounded_res.reasoning
            )
            self.db.add(sa)
            self.db.flush()
            skill_assessment_records.append(sa)

            # Record Citation
            if grounded_res.evidence_snippet and grounded_res.evidence_snippet != "No relevant resume evidence was retrieved.":
                matching_chunk_id = evidence_list[0].chunk_id if evidence_list else None
                citation = EvidenceCitation(
                    skill_assessment_id=sa.id,
                    chunk_id=matching_chunk_id,
                    snippet=grounded_res.evidence_snippet,
                    source_section=grounded_res.source_section,
                    page_number=grounded_res.page_number,
                    similarity_score=grounded_res.similarity_score,
                    is_verified_in_source=grounded_res.is_verified_in_source
                )
                self.db.add(citation)
            else:
                limitations_disclosures.append(
                    f"Requirement '{grounded_res.requirement_text}' is not explicitly evidenced in the uploaded resume."
                )

        # Step 5: Deterministic Match Score Calculation
        overall_score, mand_cov, pref_cov, score_notes = calculate_transparent_match_score(assessment_dicts_for_scoring)
        analysis.overall_match_score = overall_score
        analysis.mandatory_coverage = mand_cov
        analysis.preferred_coverage = pref_cov
        analysis.summary = score_notes

        # Limitations & Information Gaps disclosure
        limitations_disclosures.append(
            "Analysis is constrained exclusively to the textual evidence extracted from the provided resume and job description. "
            "Unlisted skills, non-textual portfolio artifacts, and verbal communication competencies cannot be evaluated."
        )
        analysis.limitations = limitations_disclosures

        # Step 6: Personalized Learning Roadmap Generation
        roadmap_items = self.roadmap_generator.generate_roadmap(assessment_dicts_for_scoring, effective_title)
        for r in roadmap_items:
            li = LearningItem(
                analysis_id=analysis.id,
                skill_name=r.skill_name,
                priority=r.priority,
                why_it_matters=r.why_it_matters,
                prerequisites=r.prerequisites,
                suggested_tasks=r.suggested_tasks,
                mini_project=r.mini_project,
                completion_criterion=r.completion_criterion,
                estimated_duration=r.estimated_duration
            )
            self.db.add(li)

        # Step 7: Role-Specific & Resume-Grounded Interview Questions
        questions = self.interview_generator.generate_questions(
            skill_assessments=assessment_dicts_for_scoring,
            resume_text=resume.extracted_text,
            job_title=effective_title,
            difficulty_filter="mixed"
        )
        for q in questions:
            iq = InterviewQuestion(
                analysis_id=analysis.id,
                question=q.question,
                category=q.category,
                difficulty=q.difficulty,
                relevance_rationale=q.relevance_rationale,
                source_type=q.source_type,
                key_concepts=q.key_concepts,
                answer_guidance=q.answer_guidance
            )
            self.db.add(iq)

        analysis.status = "completed"
        self.db.commit()
        self.db.refresh(analysis)

        return analysis
