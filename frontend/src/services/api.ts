import axios from 'axios';
import {
  ResumePreview,
  Analysis,
  AnalysisSummary,
  InterviewQuestion,
  EvaluationRun,
  HealthStatus
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadResume = async (file: File): Promise<ResumePreview> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ResumePreview>('/resumes/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const createAnalysis = async (data: {
  resume_id: string;
  job_description_raw: string;
  job_title?: string;
  company_name?: string;
  experience_level?: string;
}): Promise<Analysis> => {
  const response = await api.post<Analysis>('/analyses', data);
  return response.data;
};

export const listAnalyses = async (): Promise<AnalysisSummary[]> => {
  const response = await api.get<AnalysisSummary[]>('/analyses');
  return response.data;
};

export const getAnalysis = async (id: string): Promise<Analysis> => {
  const response = await api.get<Analysis>(`/analyses/${id}`);
  return response.data;
};

export const deleteAnalysis = async (id: string): Promise<void> => {
  await api.delete(`/analyses/${id}`);
};

export const regenerateQuestions = async (
  analysisId: string,
  difficulty: 'easy' | 'medium' | 'hard' | 'mixed'
): Promise<InterviewQuestion[]> => {
  const response = await api.post<InterviewQuestion[]>(
    `/analyses/${analysisId}/questions/regenerate`,
    { difficulty }
  );
  return response.data;
};

export const runEvaluation = async (): Promise<EvaluationRun> => {
  const response = await api.post<EvaluationRun>('/evaluations/run');
  return response.data;
};

export const getLatestEvaluation = async (): Promise<EvaluationRun> => {
  const response = await api.get<EvaluationRun>('/evaluations/results/latest');
  return response.data;
};

export const getHealth = async (): Promise<HealthStatus> => {
  const response = await api.get<HealthStatus>('/health');
  return response.data;
};

export default api;
