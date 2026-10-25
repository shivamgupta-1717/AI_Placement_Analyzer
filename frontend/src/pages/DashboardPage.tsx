import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  FilePlus, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  FolderSearch,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { listAnalyses } from '../services/api';
import { AnalysisSummary } from '../types';

export const DashboardPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAnalyses();
      setAnalyses(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load analyses from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Compute real metrics from valid user analyses
  const totalAnalyses = analyses.length;
  const validScoredAnalyses = analyses.filter(a => a.overall_match_score !== null && a.overall_match_score !== undefined);
  const avgScore = validScoredAnalyses.length > 0
    ? Math.round(validScoredAnalyses.reduce((acc, curr) => acc + (curr.overall_match_score || 0), 0) / validScoredAnalyses.length)
    : null;

  const totalDemonstrated = analyses.reduce((acc, curr) => acc + (curr.demonstrated_count || 0), 0);
  const totalMissingGaps = analyses.reduce((acc, curr) => acc + (curr.missing_count || 0), 0);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-slate-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="h-28 bg-slate-200 rounded-2xl"></div>
            <div className="h-28 bg-slate-200 rounded-2xl"></div>
            <div className="h-28 bg-slate-200 rounded-2xl"></div>
            <div className="h-28 bg-slate-200 rounded-2xl"></div>
          </div>
          <div className="h-64 bg-slate-200 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-center max-w-lg mx-auto">
          <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-3" />
          <h3 className="font-bold text-rose-900 text-lg">Unable to Load Dashboard</h3>
          <p className="text-sm text-rose-700 mt-1 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="inline-flex items-center gap-2 px-4 py-2 bg-rose-600 text-white rounded-lg text-sm font-medium hover:bg-rose-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Placement Preparation Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time analytics and evidence-grounded alignment summaries from your uploaded documents.
          </p>
        </div>

        <Link
          to="/new-analysis"
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl shadow-sm transition-colors text-sm"
        >
          <FilePlus className="w-4 h-4" />
          <span>New Resume Analysis</span>
        </Link>
      </div>

      {/* Analytics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Analyses</span>
            <BarChart3 className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{totalAnalyses}</div>
          <p className="text-xs text-slate-400 mt-1">Evaluated against role requirements</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Average Match</span>
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">
            {avgScore !== null ? `${avgScore}%` : 'N/A'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Calculated from valid evidence scores</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Demonstrated Skills</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-600">{totalDemonstrated}</div>
          <p className="text-xs text-slate-400 mt-1">Directly evidenced in resumes</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Missing Skill Gaps</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-3xl font-extrabold text-rose-600">{totalMissingGaps}</div>
          <p className="text-xs text-slate-400 mt-1">Targeted in roadmap plans</p>
        </div>
      </div>

      {/* Main Content Area */}
      {analyses.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-2xl mx-auto shadow-2xs">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4">
            <FolderSearch className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2">No Analyses Yet</h3>
          <p className="text-sm text-slate-500 mb-6 leading-relaxed">
            Get started by uploading your resume (PDF or DOCX) and providing a job description.
            The system will analyze required skills, extract evidence, and compute your weighted match score.
          </p>
          <Link
            to="/new-analysis"
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl text-sm shadow-sm transition-colors"
          >
            <FilePlus className="w-4 h-4" />
            <span>Start Your First Analysis</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-base">Recent Role Analyses</h3>
            <Link to="/history" className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1">
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100">
            {analyses.slice(0, 5).map((a) => (
              <div key={a.id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/60 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Link to={`/analyses/${a.id}`} className="font-bold text-slate-900 hover:text-indigo-600 text-base">
                      {a.job_title || 'Untitled Target Role'}
                    </Link>
                    {a.company_name && (
                      <span className="text-xs text-slate-500 font-medium">at {a.company_name}</span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span>Resume: <strong className="text-slate-700">{a.resume_filename}</strong></span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(a.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-lg font-bold text-slate-900">
                      {a.overall_match_score !== null && a.overall_match_score !== undefined ? `${Math.round(a.overall_match_score)}%` : 'N/A'}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {a.demonstrated_count} demonstrated / {a.missing_count} gaps
                    </div>
                  </div>

                  <Link
                    to={`/analyses/${a.id}`}
                    className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                  >
                    View Results
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
