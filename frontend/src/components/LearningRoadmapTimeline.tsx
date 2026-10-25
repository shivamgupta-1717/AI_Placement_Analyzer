import React from 'react';
import { 
  Compass, 
  Clock, 
  CheckCircle, 
  Layers, 
  Terminal, 
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { LearningItem } from '../types';

interface LearningRoadmapTimelineProps {
  items: LearningItem[];
}

export const LearningRoadmapTimeline: React.FC<LearningRoadmapTimelineProps> = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-8 border border-slate-200 text-center">
        <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
        <h4 className="font-bold text-slate-800 text-lg">No Critical Skill Gaps Detected</h4>
        <p className="text-sm text-slate-500 max-w-md mx-auto mt-1">
          Your resume demonstrates strong textual alignment with the key requirements of this role.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Ethical preparation reminder banner */}
      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-xs text-amber-900">
        <ShieldAlert className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-950">Ethical Placement Preparation Rule: </span>
          <span>
            Never add a missing skill to your resume merely because it is listed in the job description.
            Only add it after completing hands-on code exercises and when you can confidently explain your design choices during technical interviews.
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {items.map((item, index) => (
          <div 
            key={item.id || index}
            className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm transition-all hover:border-slate-300"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-3">
                <span className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center">
                  {index + 1}
                </span>
                <h4 className="font-bold text-slate-900 text-lg">{item.skill_name}</h4>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                  item.priority === 'high' 
                    ? 'bg-rose-50 text-rose-700 border border-rose-200' 
                    : 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                }`}>
                  {item.priority === 'high' ? 'High Priority (Mandatory)' : 'Medium Priority'}
                </span>

                <div className="flex items-center gap-1 text-xs text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full font-medium">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{item.estimated_duration}</span>
                </div>
              </div>
            </div>

            <p className="text-sm text-slate-600 mb-4 leading-relaxed">
              {item.why_it_matters}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-slate-100 text-xs">
              {/* Prerequisites & Tasks */}
              <div className="space-y-3">
                {item.prerequisites && item.prerequisites.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-700 block mb-1">Prerequisites:</span>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-600">
                      {item.prerequisites.map((p, pIdx) => (
                        <li key={pIdx}>{p}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div>
                  <span className="font-semibold text-slate-700 block mb-1">Actionable Learning Tasks:</span>
                  <ul className="space-y-1 text-slate-600">
                    {item.suggested_tasks.map((task, tIdx) => (
                      <li key={tIdx} className="flex items-start gap-1.5">
                        <ArrowRight className="w-3 h-3 text-indigo-500 flex-shrink-0 mt-0.5" />
                        <span>{task}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Practical Project & Criterion */}
              <div className="space-y-3 bg-slate-50 rounded-xl p-3.5 border border-slate-200/60">
                <div>
                  <div className="flex items-center gap-1.5 text-indigo-700 font-semibold mb-1">
                    <Terminal className="w-3.5 h-3.5" />
                    <span>Hands-On Mini Project:</span>
                  </div>
                  <p className="text-slate-700 leading-relaxed">
                    {item.mini_project}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-200/60">
                  <div className="flex items-center gap-1.5 text-emerald-700 font-semibold mb-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Measurable Completion Criterion:</span>
                  </div>
                  <p className="text-slate-600">
                    {item.completion_criterion}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
