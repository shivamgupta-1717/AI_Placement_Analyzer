export interface ResumePreview {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  extracted_text_preview: string;
  full_text_length: number;
  detected_sections: string[];
  chunk_count: number;
  created_at: string;
}

export interface EvidenceCitation {
  id: string;
  chunk_id?: string;
  snippet: string;
  source_section?: string;
  page_number?: string;
  similarity_score?: number;
  is_verified_in_source: boolean;
}

export interface SkillAssessment {
  id: string;
  requirement_id?: string;
  requirement_text: string;
  category: string;
  priority: 'mandatory' | 'preferred';
  classification: 'Demonstrated' | 'Partially demonstrated' | 'Not found in resume' | 'Uncertain';
  confidence: number;
  reasoning: string;
  citations: EvidenceCitation[];
}

export interface LearningItem {
  id: string;
  skill_name: string;
  priority: 'high' | 'medium' | 'low';
  why_it_matters: string;
  prerequisites: string[];
  suggested_tasks: string[];
  mini_project: string;
  completion_criterion: string;
  estimated_duration: string;
}

export interface InterviewQuestion {
  id: string;
  question: string;
  category: 'core_technical' | 'coding_problem' | 'project_deep_dive' | 'scenario_based' | 'behavioral';
  difficulty: 'easy' | 'medium' | 'hard';
  relevance_rationale: string;
  source_type: string;
  key_concepts: string[];
  answer_guidance?: string;
}

export interface Analysis {
  id: string;
  resume_id: string;
  job_description_id: string;
  job_title?: string;
  company_name?: string;
  experience_level?: string;
  overall_match_score?: number | null;
  mandatory_coverage?: number | null;
  preferred_coverage?: number | null;
  summary?: string;
  limitations: string[];
  status: string;
  error_message?: string;
  created_at: string;
  skill_assessments: SkillAssessment[];
  learning_roadmap: LearningItem[];
  interview_questions: InterviewQuestion[];
}

export interface AnalysisSummary {
  id: string;
  resume_id: string;
  resume_filename: string;
  job_title?: string;
  company_name?: string;
  overall_match_score?: number | null;
  mandatory_coverage?: number | null;
  preferred_coverage?: number | null;
  demonstrated_count: number;
  missing_count: number;
  partial_count: number;
  created_at: string;
}

export interface EvaluationScenarioResult {
  scenario_id: string;
  name: string;
  requirement: string;
  expected_classification: string;
  actual_classification: string;
  passed: boolean;
  reasoning: string;
  evidence_snippet?: string;
  citation_verified: boolean;
  injection_prevented: boolean;
}

export interface EvaluationRun {
  id: string;
  dataset_version: string;
  total_test_cases: number;
  precision_at_k: number;
  recall_at_k: number;
  citation_validity_rate: number;
  classification_accuracy: number;
  unsupported_claim_rate: number;
  abstention_rate: number;
  schema_validation_rate: number;
  end_to_end_success_rate: number;
  detailed_results: EvaluationScenarioResult[];
  created_at: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  database_status: string;
  database_url: string;
  llm_provider: string;
  llm_model: string;
  embedding_provider: string;
  embedding_dimension: number;
}
