import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, 
  Trash2, 
  FileText, 
  Clock, 
  ExternalLink, 
  AlertCircle, 
  Search, 
  Briefcase,
  ArrowRight
} from 'lucide-react';
import { listAnalyses, deleteAnalysis } from '../services/api';
import { AnalysisSummary } from '../types';

export const AnalysisHistoryPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await listAnalyses();
      setAnalyses(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this analysis and all its linked records?')) {
      return;
    }
    try {
      await deleteAnalysis(id);
      setAnalyses(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      alert('Failed to delete analysis record.');
    }
  };

  const filteredAnalyses = analyses.filter(a => {
    const query = searchQuery.toLowerCase();
    const titleMatch = a.job_title?.toLowerCase().includes(query);
    const companyMatch = a.company_name?.toLowerCase().includes(query);
    const resumeMatch = a.resume_filename.toLowerCase().includes(query);
    return titleMatch || companyMatch || resumeMatch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Analysis History</h1>
          <p className="text-sm text-slate-500 mt-1">
            Review past resume evaluations, track your skill coverage over time, and compare roles.
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by role, company, or file..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-white"
          />
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-slate-200 rounded-xl animate-pulse"></div>
          ))}
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-lg mx-auto shadow-2xs">
          <History className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-bold text-slate-900 text-lg mb-1">No Analyses Found</h3>
          <p className="text-sm text-slate-500 mb-6">
            {searchQuery ? 'No results matched your search criteria.' : 'You haven’t completed any resume analyses yet.'}
          </p>
          <Link
            to="/new-analysis"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-semibold hover:bg-indigo-700 transition-colors"
          >
            <span>Start Analysis</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="divide-y divide-slate-100">
            {filteredAnalyses.map((a) => (
              <div
                key={a.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/60 transition-colors"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/analyses/${a.id}`}
                      className="font-bold text-slate-900 hover:text-indigo-600 text-base flex items-center gap-1.5"
                    >
                      <span>{a.job_title || 'Target Role Analysis'}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                    </Link>
                    {a.company_name && (
                      <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {a.company_name}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3.5 h-3.5 text-slate-400" />
                      <span>{a.resume_filename}</span>
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>{new Date(a.created_at).toLocaleDateString()}</span>
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-lg font-bold text-slate-900">
                      {a.overall_match_score !== null && a.overall_match_score !== undefined
                        ? `${Math.round(a.overall_match_score)}%`
                        : 'N/A'}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {a.demonstrated_count} demonstrated / {a.missing_count} gaps
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link
                      to={`/analyses/${a.id}`}
                      className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
                    >
                      View Results
                    </Link>

                    <button
                      onClick={(e) => handleDelete(a.id, e)}
                      title="Delete Analysis"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
