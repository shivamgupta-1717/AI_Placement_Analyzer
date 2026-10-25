import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  FileText, 
  Target, 
  HelpCircle, 
  ShieldCheck, 
  ArrowRight, 
  CheckCircle2, 
  Upload, 
  BarChart3, 
  BrainCircuit,
  Lock
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50/60 via-white to-white pt-20 pb-24 border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-6 shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Grounded RAG Architecture • Zero Hallucination Guarantee</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight sm:leading-none mb-6">
            Understand Your Resume. <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 bg-clip-text text-transparent">
              Match Your Dream Role.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-lg text-slate-600 mb-8 leading-relaxed">
            The evidence-first placement analyzer built for university students and campus placement cells.
            Extracts resume qualifications, verifies real context against job descriptions, and gives you a mathematically transparent alignment score.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/new-analysis"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium shadow-md shadow-indigo-100 transition-all text-base"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-medium transition-all text-base shadow-2xs"
            >
              <BarChart3 className="w-4 h-4 text-slate-500" />
              <span>View Dashboard</span>
            </Link>
          </div>

          {/* Value Highlights */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-14 pt-10 border-t border-slate-100 max-w-4xl mx-auto text-left">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-slate-900">4-State Skills</h4>
                <p className="text-xs text-slate-500">Demonstrated vs Missing</p>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-slate-900">Evidence Citations</h4>
                <p className="text-xs text-slate-500">Exact page & section proof</p>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-slate-900">Weighted Match</h4>
                <p className="text-xs text-slate-500">No fabricated percentages</p>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-slate-900">Security Fenced</h4>
                <p className="text-xs text-slate-500">Prompt injection shielded</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Simple Workflow */}
      <section className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-2">Simple Workflow</h2>
            <h3 className="text-3xl font-extrabold text-slate-900">How It Works</h3>
            <p className="text-sm text-slate-500 mt-2">Get from raw PDF to evidence-backed preparation in seconds.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200 text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mx-auto mb-4 shadow-sm">
                1
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Upload Resume</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Upload your PDF or DOCX file. Our document parser extracts text, detects sections, and builds semantic vector embeddings.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200 text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mx-auto mb-4 shadow-sm">
                2
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Analyze Job Description</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Paste the target job description. The system isolates mandatory from preferred qualifications and runs hybrid semantic retrieval.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200 text-center relative">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg mx-auto mb-4 shadow-sm">
                3
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Get Your Preparation Plan</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Receive grounded match analytics, actionable roadmap items with mini-projects, and role-tailored technical interview questions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-20 bg-slate-50/70 border-t border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-2">Core Capabilities</h2>
            <h3 className="text-3xl font-extrabold text-slate-900">Engineered for Accuracy & Explainability</h3>
            <p className="text-sm text-slate-500 mt-2">Not just another wrapper. An audited, grounded RAG implementation.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-all">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                <FileText className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Resume Parsing</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                PyMuPDF and python-docx text extraction with scanned PDF detection, section header normalization, and semantic chunking.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-all">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
                <Target className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Skill Gap Detection</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Distinguishes Demonstrated from Missing skills with strict evidence thresholds. "Not found" never implies personal inability.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-all">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
                <HelpCircle className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Interview Preparation</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Generates questions grounded in your actual uploaded projects and mandatory job requirements. Filter by difficulty anytime.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-all">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-slate-900 mb-2">Grounded AI & Abstention</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Strict post-generation citation verification against original resume chunks, prompt injection defenses, and zero hallucinations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-white border-t border-slate-200">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h3 className="text-3xl font-extrabold text-slate-900 mb-4">Ready to Benchmark Your Placement Readiness?</h3>
          <p className="text-slate-600 text-base mb-8 max-w-xl mx-auto">
            Upload your resume now to inspect evidence citations and calculate your weighted alignment score.
          </p>
          <Link
            to="/new-analysis"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium shadow-md transition-all text-base"
          >
            <span>Start Analysis Now</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
};
