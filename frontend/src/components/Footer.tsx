import React from 'react';
import { Shield, Sparkles, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 bg-white py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-900">AI Placement Analyzer</span>
            </div>
            <p className="text-sm text-slate-500 max-w-sm mb-4 leading-relaxed">
              Evidence-based placement preparation using Retrieval-Augmented Generation (RAG).
              Grounded assessments, hallucination prevention, and transparent alignment scoring for university candidates.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Shield className="w-3.5 h-3.5 text-emerald-600" />
              <span>Prompt injection defended & strict citation verification enabled</span>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Platform</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><Link to="/dashboard" className="hover:text-indigo-600">Dashboard</Link></li>
              <li><Link to="/new-analysis" className="hover:text-indigo-600">Analyze Resume</Link></li>
              <li><Link to="/history" className="hover:text-indigo-600">Past Analyses</Link></li>
              <li><Link to="/evaluation" className="hover:text-indigo-600">RAG Reliability Metrics</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">Privacy & Ethics</h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><Link to="/settings" className="hover:text-indigo-600">Data Retention Policy</Link></li>
              <li><Link to="/settings" className="hover:text-indigo-600">Document Deletion Controls</Link></li>
              <li><a href="/docs" target="_blank" rel="noreferrer" className="hover:text-indigo-600">FastAPI OpenAPI Spec</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} AI Placement Analyzer. Built with FastAPI, pgvector & React.</p>
          <p className="text-slate-400">Not a hiring guarantee. Resume-to-JD alignment tool.</p>
        </div>
      </div>
    </footer>
  );
};
