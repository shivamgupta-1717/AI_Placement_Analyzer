import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  Quote, 
  ShieldCheck, 
  AlertTriangle 
} from 'lucide-react';
import { SkillAssessment } from '../types';

interface SkillGapCardProps {
  assessment: SkillAssessment;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({ assessment }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusBadge = () => {
    switch (assessment.classification) {
      case 'Demonstrated':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            Demonstrated
          </span>
        );
      case 'Partially demonstrated':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
            Partially Demonstrated
          </span>
        );
      case 'Not found in resume':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            Not Found in Resume
          </span>
        );
      case 'Uncertain':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
            Uncertain / Ambiguous
          </span>
        );
    }
  };

  const hasCitations = assessment.citations && assessment.citations.length > 0;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all hover:border-slate-300">
      <div className="p-4 sm:p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="font-semibold text-slate-900 text-base">{assessment.requirement_text}</h4>
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 uppercase tracking-wide">
              {(assessment.category || '').replace('_', ' ')}
            </span>
            <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
              assessment.priority === 'mandatory' 
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold' 
                : 'bg-slate-50 text-slate-600'
            }`}>
              {assessment.priority === 'mandatory' ? 'Mandatory' : 'Preferred'}
            </span>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {getStatusBadge()}
          </div>
        </div>

        <p className="text-sm text-slate-600 leading-relaxed mt-2 mb-3">
          {assessment.reasoning}
        </p>

        {/* Evidence citation toggle */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
          <div className="text-slate-500">
            {assessment.classification === 'Not found in resume' ? (
              <span className="italic text-slate-400">
                Note: "Not found" means not evidenced in document, not that candidate lacks the ability.
              </span>
            ) : hasCitations ? (
              <span className="text-slate-600 font-medium">
                {assessment.citations.length} cited source snippet{assessment.citations.length > 1 ? 's' : ''} available
              </span>
            ) : (
              <span className="text-slate-400 italic">No direct citation snippet</span>
            )}
          </div>

          {hasCitations && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium py-1 px-2 rounded hover:bg-indigo-50 transition-colors"
            >
              <span>{isExpanded ? 'Hide Evidence' : 'View Source Evidence'}</span>
              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Expandable Evidence Drawer */}
      {isExpanded && hasCitations && (
        <div className="bg-slate-50/80 border-t border-slate-200 p-4 space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Quote className="w-3.5 h-3.5 text-indigo-600" />
            <span>Retrieved Evidence from Resume</span>
          </div>

          {assessment.citations.map((citation, idx) => (
            <div key={citation.id || idx} className="bg-white rounded-lg p-3.5 border border-slate-200 text-xs shadow-2xs">
              <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                    Section: {citation.source_section || 'Resume'}
                  </span>
                  {citation.page_number && (
                    <span className="text-slate-500">Page {citation.page_number}</span>
                  )}
                </div>

                <div className="flex items-center gap-1.5">
                  {citation.is_verified_in_source ? (
                    <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[10px] font-semibold border border-emerald-200">
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                      Verified Grounding
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-50 px-2 py-0.5 rounded text-[10px] font-semibold border border-amber-200">
                      <AlertTriangle className="w-3 h-3 text-amber-600" />
                      Unverified
                    </span>
                  )}
                  {citation.similarity_score !== undefined && citation.similarity_score !== null && (
                    <span className="text-slate-400 font-mono text-[10px]">
                      sim: {(citation.similarity_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>

              <blockquote className="text-slate-700 italic border-l-2 border-indigo-400 pl-3 py-1 font-serif text-[13px] leading-relaxed">
                "{citation.snippet}"
              </blockquote>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
