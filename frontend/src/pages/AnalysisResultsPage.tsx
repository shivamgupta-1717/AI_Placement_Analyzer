import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  BarChart3, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  HelpCircle, 
  Compass, 
  MessageSquare, 
  ShieldAlert, 
  Trash2, 
  RefreshCw, 
  ArrowLeft,
  Briefcase,
  Building2,
  Clock,
  Layers,
  Sparkles,
  FileText
} from 'lucide-react';
import { getAnalysis, deleteAnalysis, regenerateQuestions } from '../services/api';
import { Analysis, SkillAssessment, InterviewQuestion } from '../types';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { SkillGapCard } from '../components/SkillGapCard';
import { LearningRoadmapTimeline } from '../components/LearningRoadmapTimeline';

export const AnalysisResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active section tab
  const [activeTab, setActiveTab] = useState<'skills' | 'roadmap' | 'questions' | 'limitations'>('skills');

  // Skill filter
  const [skillFilter, setSkillFilter] = useState<'all' | 'Demonstrated' | 'Partially demonstrated' | 'Not found in resume' | 'Uncertain'>('all');

  // Question regeneration state
  const [questionDifficulty, setQuestionDifficulty] = useState<'easy' | 'medium' | 'hard' | 'mixed'>('mixed');
  const [isRegeneratingQuestions, setIsRegeneratingQuestions] = useState(false);

  const fetchAnalysisDetails = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load analysis results.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysisDetails();
  }, [id]);

  const handleDelete = async () => {
    if (!id || !window.confirm('Are you sure you want to delete this analysis? All associated skills, evidence citations, roadmap, and questions will be permanently purged.')) {
      return;
    }
    try {
      await deleteAnalysis(id);
      navigate('/history');
    } catch (err) {
      alert('Failed to delete analysis.');
    }
  };

  const handleRegenerateQuestions = async () => {
    if (!id) return;
    setIsRegeneratingQuestions(true);
    try {
      const updatedQuestions = await regenerateQuestions(id, questionDifficulty);
      setAnalysis(prev => prev ? { ...prev, interview_questions: updatedQuestions } : null);
    } catch (err) {
      alert('Failed to regenerate questions.');
    } finally {
      setIsRegeneratingQuestions(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-6 bg-slate-200 rounded w-1/5"></div>
          <div className="h-10 bg-slate-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 h-64 bg-slate-200 rounded-2xl"></div>
            <div className="lg:col-span-2 h-64 bg-slate-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-12 h-12 text-rose-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-900 mb-2">Analysis Result Not Found</h2>
        <p className="text-sm text-slate-500 mb-6">{error || 'This analysis session does not exist or was deleted.'}</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  // Filter skills
  const filteredSkills = analysis.skill_assessments.filter(sa => {
    if (skillFilter === 'all') return true;
    return sa.classification === skillFilter;
  });

  const demonstratedCount = analysis.skill_assessments.filter(sa => sa.classification === 'Demonstrated').length;
  const partialCount = analysis.skill_assessments.filter(sa => sa.classification === 'Partially demonstrated').length;
  const missingCount = analysis.skill_assessments.filter(sa => sa.classification === 'Not found in resume').length;
  const uncertainCount = analysis.skill_assessments.filter(sa => sa.classification === 'Uncertain').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </Link>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDelete}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg border border-rose-200 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete Analysis</span>
          </button>
        </div>
      </div>

      {/* Target Role Overview Banner */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-2xl font-extrabold text-slate-900">{analysis.job_title || 'Target Role Analysis'}</h1>
              {analysis.company_name && (
                <span className="text-sm font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                  {analysis.company_name}
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-2">
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                <span>{analysis.experience_level || 'Campus Placement'}</span>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Analyzed on {new Date(analysis.created_at).toLocaleDateString()}</span>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Grounded RAG Audit Complete</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 1: Score & Coverage Gauge */}
      <div className="mb-8">
        <MatchScoreGauge
          score={analysis.overall_match_score}
          mandatoryCoverage={analysis.mandatory_coverage}
          preferredCoverage={analysis.preferred_coverage}
          demonstratedCount={demonstratedCount}
          partialCount={partialCount}
          missingCount={missingCount}
        />
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <nav className="flex space-x-8 overflow-x-auto">
          <button
            onClick={() => setActiveTab('skills')}
            className={`py-3.5 text-sm font-bold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'skills'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Skills & Evidence Audit ({analysis.skill_assessments.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('roadmap')}
            className={`py-3.5 text-sm font-bold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'roadmap'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Preparation Roadmap ({analysis.learning_roadmap.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('questions')}
            className={`py-3.5 text-sm font-bold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'questions'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Role Interview Questions ({analysis.interview_questions.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('limitations')}
            className={`py-3.5 text-sm font-bold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'limitations'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Limitations & Disclosures</span>
          </button>
        </nav>
      </div>

      {/* Tab 1: Skills & Evidence Audit */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setSkillFilter('all')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                skillFilter === 'all'
                  ? 'bg-slate-900 text-white'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              All Requirements ({analysis.skill_assessments.length})
            </button>
            <button
              onClick={() => setSkillFilter('Demonstrated')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                skillFilter === 'Demonstrated'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-white border border-slate-200 text-emerald-700 hover:bg-emerald-50'
              }`}
            >
              Demonstrated ({demonstratedCount})
            </button>
            <button
              onClick={() => setSkillFilter('Partially demonstrated')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                skillFilter === 'Partially demonstrated'
                  ? 'bg-amber-600 text-white'
                  : 'bg-white border border-slate-200 text-amber-700 hover:bg-amber-50'
              }`}
            >
              Partially Demonstrated ({partialCount})
            </button>
            <button
              onClick={() => setSkillFilter('Not found in resume')}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                skillFilter === 'Not found in resume'
                  ? 'bg-rose-600 text-white'
                  : 'bg-white border border-slate-200 text-rose-700 hover:bg-rose-50'
              }`}
            >
              Missing Gaps ({missingCount})
            </button>
            {uncertainCount > 0 && (
              <button
                onClick={() => setSkillFilter('Uncertain')}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                  skillFilter === 'Uncertain'
                    ? 'bg-slate-700 text-white'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                Uncertain ({uncertainCount})
              </button>
            )}
          </div>

          {/* Skill Cards List */}
          <div className="space-y-4">
            {filteredSkills.map((sa) => (
              <SkillGapCard key={sa.id} assessment={sa} />
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Learning Roadmap */}
      {activeTab === 'roadmap' && (
        <LearningRoadmapTimeline items={analysis.learning_roadmap} />
      )}

      {/* Tab 3: Role Interview Questions */}
      {activeTab === 'questions' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-5 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Practice Role-Specific Interview Questions</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Grounded in your resume projects and mandatory job requirements.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={questionDifficulty}
                onChange={(e) => setQuestionDifficulty(e.target.value as any)}
                className="px-3 py-1.5 text-xs border border-slate-200 rounded-lg bg-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
              >
                <option value="mixed">Mixed Difficulty</option>
                <option value="easy">Easy Level</option>
                <option value="medium">Medium Level</option>
                <option value="hard">Hard Level</option>
              </select>

              <button
                onClick={handleRegenerateQuestions}
                disabled={isRegeneratingQuestions}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRegeneratingQuestions ? 'animate-spin' : ''}`} />
                <span>Regenerate</span>
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {analysis.interview_questions.map((q, idx) => (
              <div key={q.id || idx} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center">
                      Q{idx + 1}
                    </span>
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 uppercase tracking-wide">
                      {(q.category || '').replace('_', ' ')}
                    </span>
                    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                      q.difficulty === 'hard'
                        ? 'bg-rose-50 text-rose-700 border border-rose-200'
                        : q.difficulty === 'medium'
                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {(q.difficulty || 'medium').toUpperCase()}
                    </span>
                  </div>

                  <span className="text-[11px] text-slate-400 italic">
                    Source: {(q.source_type || '').replace('_', ' ')}
                  </span>
                </div>

                <h4 className="font-bold text-slate-900 text-base leading-snug">{q.question}</h4>

                <p className="text-xs text-slate-500 leading-relaxed">
                  <strong className="text-slate-700">Why it's relevant: </strong>
                  {q.relevance_rationale}
                </p>

                {q.key_concepts && q.key_concepts.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Key Concepts:</span>
                    {q.key_concepts.map((concept, cIdx) => (
                      <span key={cIdx} className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-50 border border-slate-200 text-slate-600">
                        {concept}
                      </span>
                    ))}
                  </div>
                )}

                {q.answer_guidance && (
                  <div className="bg-indigo-50/50 rounded-xl p-3 border border-indigo-100 text-xs text-indigo-950">
                    <span className="font-bold block mb-0.5">Answer Strategy & Guidance:</span>
                    <p className="text-indigo-900/90 leading-relaxed">{q.answer_guidance}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Limitations & Disclosures */}
      {activeTab === 'limitations' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center gap-2 text-amber-700 font-bold text-base">
            <ShieldAlert className="w-5 h-5 text-amber-600" />
            <h3>Audited Limitations & Information Gaps</h3>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            In accordance with grounded AI engineering standards, every analysis reports what information is missing, uncertain, or impossible to verify from the provided documents.
          </p>

          <ul className="space-y-2 text-xs text-slate-700 pt-2 border-t border-slate-100">
            {analysis.limitations.map((lim, lIdx) => (
              <li key={lIdx} className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200/60">
                <span className="text-amber-600 font-bold">•</span>
                <span>{lim}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
