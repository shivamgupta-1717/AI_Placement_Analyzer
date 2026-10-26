import React, { useEffect, useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Shield, 
  Cpu, 
  Database, 
  Lock, 
  Trash2, 
  CheckCircle2, 
  AlertCircle,
  FileText
} from 'lucide-react';
import { getHealth } from '../services/api';
import { HealthStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings & Privacy Policy</h1>
        <p className="text-sm text-slate-500 mt-1">
          Transparency into document storage, embedding providers, data retention, and privacy safeguards.
        </p>
      </div>

      {/* Active System Architecture Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-600" />
          <h2 className="font-bold text-slate-900 text-base">Active RAG Runtime Configuration</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Information on current backend inference and vector retrieval engine. API keys are managed exclusively on the server and are never exposed to the browser.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
              LLM Generation Engine
            </span>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <strong className="text-sm text-slate-900">
                {health && typeof health === 'object' && health.llm_provider
                  ? `${(health.llm_provider || '').toUpperCase()} (${health.llm_model || 'default'})`
                  : 'Connecting / Offline Mode'}
              </strong>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              Supports Google Gemini, OpenAI GPT-4o, and built-in offline mock modes via environment variables.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
              Vector Storage & Retrieval
            </span>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-600" />
              <strong className="text-sm text-slate-900">
                {health && typeof health === 'object' && health.database_url
                  ? `${health.database_url} (${health.embedding_dimension || 768}-dim)`
                  : 'SQLite / Embedded Vectors'}
              </strong>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              PostgreSQL with pgvector for high-performance cosine similarity, with seamless local SQLite portability.
            </p>
          </div>
        </div>
      </div>

      {/* Data Retention & Privacy Notice Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-emerald-600" />
          <h2 className="font-bold text-slate-900 text-base">Document Retention & Privacy Notice</h2>
        </div>

        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
          <div className="p-3.5 bg-emerald-50/60 border border-emerald-100 rounded-xl">
            <strong className="text-emerald-950 block mb-1">1. Student Document Privacy:</strong>
            <p className="text-emerald-900/90">
              Uploaded resumes are stored exclusively for extracting skills and generating placement recommendations.
              Raw resume binaries are not distributed to external public repositories or training datasets.
            </p>
          </div>

          <div className="p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl">
            <strong className="text-indigo-950 block mb-1">2. Document Retention Policy:</strong>
            <p className="text-indigo-900/90">
              Extracted chunks and vector embeddings are associated with your individual analysis ID.
              Analyses are preserved until deleted by the user or purged in accordance with university placement cycle retention guidelines (default: 30 days).
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200/60 rounded-xl">
            <strong className="text-slate-900 block mb-1">3. Complete Cascade Deletion:</strong>
            <p className="text-slate-600">
              When you delete an analysis from the History tab, the action triggers a cascade purge across all relational tables:
              removing all resume chunks, vector embeddings, skill assessments, evidence citations, roadmap items, and interview questions.
            </p>
          </div>
        </div>
      </div>

      {/* Administrative Setup Instructions */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-3">
        <div className="flex items-center gap-2">
          <Lock className="w-5 h-5 text-slate-700" />
          <h2 className="font-bold text-slate-900 text-base">Server Configuration Guide for Administrators</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          To switch between live cloud providers and local development, configure your server <code className="px-1.5 py-0.5 rounded bg-slate-100 font-mono text-[11px]">.env</code> file:
        </p>

        <div className="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-mono space-y-1 overflow-x-auto">
          <p className="text-slate-400"># Database (PostgreSQL with pgvector or SQLite)</p>
          <p>DATABASE_URL=postgresql://postgres:password@localhost:5432/placement_analyzer</p>
          <p className="text-slate-400 pt-2"># LLM Provider Configuration</p>
          <p>LLM_PROVIDER=gemini  # or "openai", "mock"</p>
          <p>GEMINI_API_KEY=your_gemini_api_key_here</p>
          <p className="text-slate-400 pt-2"># Vector Embeddings</p>
          <p>EMBEDDING_PROVIDER=gemini</p>
          <p>EMBEDDING_MODEL=models/text-embedding-004</p>
          <p>EMBEDDING_DIMENSION=768</p>
        </div>
      </div>
    </div>
  );
};
