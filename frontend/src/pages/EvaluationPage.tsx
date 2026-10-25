import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  Play, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Info, 
  FileCode,
  Lock,
  Target
} from 'lucide-react';
import { runEvaluation, getLatestEvaluation } from '../services/api';
import { EvaluationRun } from '../types';

export const EvaluationPage: React.FC = () => {
  const [evaluation, setEvaluation] = useState<EvaluationRun | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLatestEvaluation()
      .then(setEvaluation)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleRunEvaluation = async () => {
    setIsRunning(true);
    try {
      const result = await runEvaluation();
      setEvaluation(result);
    } catch (err) {
      alert('Evaluation benchmark failed to run.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-slate-900">RAG Reliability & Benchmark Evaluation</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Audited Labeled Dataset
            </span>
          </div>
          <p className="text-sm text-slate-500">
            Systematic verification of retrieval quality, evidence grounding, abstention behavior, and prompt injection defense across 10 deterministic test scenarios.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={isRunning}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl shadow-sm transition-colors text-sm disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Running 10 Scenarios...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Execute Live Benchmark</span>
            </>
          )}
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-slate-200 rounded-2xl animate-pulse"></div>
            ))}
          </div>
          <div className="h-80 bg-slate-200 rounded-2xl animate-pulse"></div>
        </div>
      ) : !evaluation ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-lg mx-auto">
          <ShieldCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-bold text-slate-900 text-lg mb-1">No Evaluation Records Yet</h3>
          <p className="text-sm text-slate-500 mb-6">
            Execute the deterministic evaluation benchmark to compute live Precision@K, Recall@K, and Abstention metrics.
          </p>
          <button
            onClick={handleRunEvaluation}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700"
          >
            Run Benchmark
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Metrics KPI Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                Classification Accuracy
              </span>
              <div className="text-2xl font-extrabold text-indigo-600">
                {evaluation.classification_accuracy}%
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Ground-truth label matching</p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                Evidence Citation Validity
              </span>
              <div className="text-2xl font-extrabold text-emerald-600">
                {evaluation.citation_validity_rate}%
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Verified quotes in resume chunks</p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                Abstention on Missing
              </span>
              <div className="text-2xl font-extrabold text-emerald-600">
                {evaluation.abstention_rate}%
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Zero hallucinated claims</p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                Unsupported Claim Rate
              </span>
              <div className="text-2xl font-extrabold text-emerald-600">
                {evaluation.unsupported_claim_rate}%
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Target is 0.0% (Zero false matches)</p>
            </div>
          </div>

          {/* Secondary Metrics Bar */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-500 block">Retrieval Precision@K:</span>
              <strong className="text-slate-900 font-bold text-sm">{evaluation.precision_at_k}%</strong>
            </div>
            <div>
              <span className="text-slate-500 block">Retrieval Recall@K:</span>
              <strong className="text-slate-900 font-bold text-sm">{evaluation.recall_at_k}%</strong>
            </div>
            <div>
              <span className="text-slate-500 block">Schema Validation Rate:</span>
              <strong className="text-slate-900 font-bold text-sm">{evaluation.schema_validation_rate}%</strong>
            </div>
            <div>
              <span className="text-slate-500 block">End-to-End Success Rate:</span>
              <strong className="text-slate-900 font-bold text-sm">{evaluation.end_to_end_success_rate}%</strong>
            </div>
          </div>

          {/* Scenario Details Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="p-5 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Deterministic Test Scenarios ({evaluation.detailed_results.length})</h3>
                <p className="text-xs text-slate-500 mt-0.5">Audited against labeled expectations in `evaluation_dataset.json`</p>
              </div>
              <span className="text-xs text-slate-400 font-mono">Dataset v{evaluation.dataset_version}</span>
            </div>

            <div className="divide-y divide-slate-100">
              {evaluation.detailed_results.map((res, idx) => (
                <div key={idx} className="p-5 hover:bg-slate-50/50 transition-colors space-y-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      {res.passed ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
                      )}
                      <div>
                        <span className="font-bold text-slate-900 text-sm">{res.name}</span>
                        <span className="ml-2 font-mono text-[11px] text-slate-400">[{res.scenario_id}]</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500">
                        Expected: <strong className="text-slate-700">{res.expected_classification}</strong>
                      </span>
                      <span>→</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        res.actual_classification === res.expected_classification
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}>
                        Actual: {res.actual_classification}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 pl-7 leading-relaxed">
                    {res.reasoning}
                  </p>

                  <div className="pl-7 pt-1 flex flex-wrap items-center gap-2 text-[11px]">
                    {res.citation_verified && (
                      <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        Citation Grounding Verified
                      </span>
                    )}

                    {res.injection_prevented && (
                      <span className="inline-flex items-center gap-1 text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                        <Lock className="w-3 h-3 text-indigo-600" />
                        Prompt Injection Fenced
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
