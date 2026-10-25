import React from 'react';
import { Info, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';

interface MatchScoreGaugeProps {
  score: number | null | undefined;
  mandatoryCoverage: number | null | undefined;
  preferredCoverage: number | null | undefined;
  demonstratedCount: number;
  partialCount: number;
  missingCount: number;
}

export const MatchScoreGauge: React.FC<MatchScoreGaugeProps> = ({
  score,
  mandatoryCoverage,
  preferredCoverage,
  demonstratedCount,
  partialCount,
  missingCount,
}) => {
  const hasScore = score !== null && score !== undefined;
  const numScore = hasScore ? Math.round(score) : 0;

  // Determine color theme based on score tier
  let ringColor = 'text-indigo-600';
  let badgeBg = 'bg-indigo-50 text-indigo-700 border-indigo-200';
  let tierText = 'Moderate Alignment';

  if (numScore >= 80) {
    ringColor = 'text-emerald-500';
    badgeBg = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    tierText = 'Strong Alignment';
  } else if (numScore < 50) {
    ringColor = 'text-amber-500';
    badgeBg = 'bg-amber-50 text-amber-700 border-amber-200';
    tierText = 'Significant Skill Gaps';
  }

  // SVG circular progress calculation
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = hasScore ? circumference - (numScore / 100) * circumference : circumference;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-900 text-base">Resume–JD Alignment Score</h3>
        <div className="group relative cursor-pointer">
          <Info className="w-4 h-4 text-slate-400 hover:text-slate-600" />
          <div className="hidden group-hover:block absolute right-0 top-6 w-72 p-3 bg-slate-900 text-white text-xs rounded-xl shadow-xl z-50 leading-relaxed">
            <p className="font-semibold mb-1 text-slate-100">Deterministic Weighted Formula:</p>
            <p className="text-slate-300 mb-2">
              Mandatory qualifications have weight 3.0, Preferred qualifications have weight 1.5. Adequacy is evaluated based on verified resume evidence.
            </p>
            <p className="text-slate-400 italic text-[11px]">
              Note: This score measures resume text alignment to the target description, NOT an interview or hiring guarantee.
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* Circular Gauge */}
        <div className="relative w-36 h-36 flex items-center justify-center flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 128 128">
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="currentColor"
              strokeWidth="10"
              className="text-slate-100"
              fill="transparent"
            />
            {hasScore && (
              <circle
                cx="64"
                cy="64"
                r={radius}
                stroke="currentColor"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                className={`${ringColor} transition-all duration-1000 ease-out`}
                fill="transparent"
              />
            )}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            {hasScore ? (
              <>
                <span className="text-3xl font-extrabold text-slate-900">{numScore}%</span>
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Match</span>
              </>
            ) : (
              <span className="text-xs font-semibold text-slate-400 text-center px-2">Insufficient Evidence</span>
            )}
          </div>
        </div>

        {/* Detailed Breakdown */}
        <div className="flex-1 w-full space-y-3">
          <div className="flex items-center justify-between">
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeBg}`}>
              {hasScore ? tierText : 'Analysis Incomplete'}
            </span>
          </div>

          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span>Mandatory Coverage</span>
                <span className="font-semibold text-slate-900">{mandatoryCoverage ?? 0}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, mandatoryCoverage ?? 0))}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span>Preferred Coverage</span>
                <span className="font-semibold text-slate-900">{preferredCoverage ?? 0}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, preferredCoverage ?? 0))}%` }}
                />
              </div>
            </div>
          </div>

          {/* Quick counts */}
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 text-center text-xs">
            <div className="bg-emerald-50/50 p-1.5 rounded-lg">
              <span className="block font-bold text-emerald-700">{demonstratedCount}</span>
              <span className="text-[10px] text-slate-500">Demonstrated</span>
            </div>
            <div className="bg-amber-50/50 p-1.5 rounded-lg">
              <span className="block font-bold text-amber-700">{partialCount}</span>
              <span className="text-[10px] text-slate-500">Partial/Weak</span>
            </div>
            <div className="bg-rose-50/50 p-1.5 rounded-lg">
              <span className="block font-bold text-rose-700">{missingCount}</span>
              <span className="text-[10px] text-slate-500">Missing Gaps</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
