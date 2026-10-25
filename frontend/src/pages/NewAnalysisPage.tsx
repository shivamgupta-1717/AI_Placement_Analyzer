import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  ArrowRight, 
  Briefcase, 
  Building2, 
  GraduationCap, 
  Layers, 
  Sparkles,
  FileCode
} from 'lucide-react';
import { uploadResume, createAnalysis } from '../services/api';
import { ResumePreview } from '../types';

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Resume state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [resumePreview, setResumePreview] = useState<ResumePreview | null>(null);

  // Job Description state
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('Campus Placement / Fresher');
  const [jobDescription, setJobDescription] = useState('');

  // Analysis execution state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisStep, setAnalysisStep] = useState(0);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await processSelectedFile(file);
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      await processSelectedFile(file);
    }
  };

  const processSelectedFile = async (file: File) => {
    setUploadError(null);
    const validExtensions = ['.pdf', '.docx'];
    const hasValidExt = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    if (!hasValidExt) {
      setUploadError('Please select a valid PDF (.pdf) or Word (.docx) document.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size exceeds the 10MB limit.');
      return;
    }

    setSelectedFile(file);
    setIsUploading(true);

    try {
      const preview = await uploadResume(file);
      setResumePreview(preview);
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail || 'Failed to upload and parse resume.');
      setSelectedFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmitAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumePreview) {
      setAnalysisError('Please upload and verify your resume first.');
      return;
    }

    if (!jobDescription || jobDescription.trim().length < 20) {
      setAnalysisError('Please enter a job description of at least 20 characters.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    // Staged progress ticker
    const interval = setInterval(() => {
      setAnalysisStep(prev => (prev < 4 ? prev + 1 : prev));
    }, 900);

    try {
      const result = await createAnalysis({
        resume_id: resumePreview.id,
        job_description_raw: jobDescription,
        job_title: jobTitle.trim() || undefined,
        company_name: companyName.trim() || undefined,
        experience_level: experienceLevel
      });
      clearInterval(interval);
      navigate(`/analyses/${result.id}`);
    } catch (err: any) {
      clearInterval(interval);
      setIsAnalyzing(false);
      setAnalysisError(err?.response?.data?.detail || 'Analysis pipeline execution failed.');
    }
  };

  const analysisSteps = [
    'Decomposing job description into structured requirements...',
    'Generating semantic vector embeddings & hybrid queries...',
    'Retrieving candidate evidence chunks with threshold filtering...',
    'Verifying citations & grounding against hallucination...',
    'Computing weighted match score & generating roadmap...'
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">New Placement Resume Analysis</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload your resume and provide a target job description to run our evidence-grounded RAG audit.
        </p>
      </div>

      <form onSubmit={handleSubmitAnalysis} className="space-y-8">
        {/* Step 1: Resume Upload Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                1
              </span>
              <h2 className="font-bold text-slate-900 text-base">Upload Your Resume</h2>
            </div>
            <span className="text-xs text-slate-400">PDF or DOCX (Max 10MB)</span>
          </div>

          {!resumePreview ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isUploading 
                  ? 'border-indigo-300 bg-indigo-50/30' 
                  : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="hidden"
              />
              {isUploading ? (
                <div className="flex flex-col items-center">
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-3" />
                  <p className="font-semibold text-slate-700 text-sm">Parsing resume & extracting sections...</p>
                  <p className="text-xs text-slate-400 mt-1">Detecting education, projects, skills, and chunks</p>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
                    <Upload className="w-6 h-6" />
                  </div>
                  <p className="font-semibold text-slate-800 text-sm">
                    Drag and drop your resume file here, or <span className="text-indigo-600">browse files</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Supports searchable PDF and Microsoft Word (.docx)</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{resumePreview.filename}</h4>
                    <p className="text-xs text-slate-500">
                      {(resumePreview.file_size / 1024).toFixed(1)} KB • {resumePreview.chunk_count} semantic chunks indexed
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    setResumePreview(null);
                    setSelectedFile(null);
                  }}
                  className="text-xs text-slate-500 hover:text-rose-600 font-medium px-2 py-1 rounded hover:bg-white transition-colors"
                >
                  Change File
                </button>
              </div>

              {/* Detected Sections */}
              {resumePreview.detected_sections && resumePreview.detected_sections.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-200/80 flex flex-wrap items-center gap-1.5">
                  <span className="text-[11px] font-semibold text-slate-500 mr-1">Detected Sections:</span>
                  {resumePreview.detected_sections.map((sec, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded text-[11px] font-medium bg-white border border-slate-200 text-slate-700">
                      {sec}
                    </span>
                  ))}
                </div>
              )}

              {/* Text Preview */}
              <div className="mt-3 pt-2">
                <span className="text-[11px] font-semibold text-slate-500 block mb-1">Extracted Text Preview:</span>
                <p className="text-xs text-slate-600 bg-white p-2.5 rounded border border-slate-200 italic font-mono leading-relaxed max-h-24 overflow-y-auto">
                  "{resumePreview.extracted_text_preview}"
                </p>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="mt-3 p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2 text-xs text-rose-700">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Step 2: Target Job Description Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
              2
            </span>
            <h2 className="font-bold text-slate-900 text-base">Target Role & Job Description</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Target Job Title <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <div className="relative">
                <Briefcase className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Full Stack Developer"
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Company Name <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <div className="relative">
                <Building2 className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="e.g. Google / Microsoft"
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Target Experience Level
              </label>
              <div className="relative">
                <GraduationCap className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                >
                  <option value="Campus Placement / Fresher">Campus Placement / Fresher</option>
                  <option value="Junior Engineer (0-2 yrs)">Junior Engineer (0-2 yrs)</option>
                  <option value="Mid Level (2-5 yrs)">Mid Level (2-5 yrs)</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-700">
                Job Description Text <span className="text-rose-500">*</span>
              </label>
              <span className={`text-[11px] ${jobDescription.length < 20 ? 'text-slate-400' : 'text-emerald-600 font-medium'}`}>
                {jobDescription.length} characters (min 20)
              </span>
            </div>
            <textarea
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job description here. Include qualifications, technical requirements, responsibilities, and preferred skills..."
              className="w-full p-3.5 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-sans leading-relaxed"
            />
          </div>
        </div>

        {/* Error message */}
        {analysisError && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-sm text-rose-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{analysisError}</span>
          </div>
        )}

        {/* Action Button & Processing Indicator */}
        <div className="pt-2">
          {isAnalyzing ? (
            <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-6 text-center space-y-3">
              <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto" />
              <h3 className="font-bold text-indigo-950 text-base">Analyzing Alignment with RAG...</h3>
              <p className="text-xs font-medium text-indigo-700 transition-all">
                {analysisSteps[analysisStep]}
              </p>
              <div className="w-48 bg-indigo-200/60 rounded-full h-1.5 mx-auto overflow-hidden">
                <div
                  className="bg-indigo-600 h-1.5 rounded-full transition-all duration-700"
                  style={{ width: `${(analysisStep + 1) * 20}%` }}
                />
              </div>
            </div>
          ) : (
            <button
              type="submit"
              disabled={!resumePreview || jobDescription.trim().length < 20}
              className={`w-full py-4 rounded-xl font-bold text-base flex items-center justify-center gap-2 shadow-md transition-all ${
                !resumePreview || jobDescription.trim().length < 20
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-100 hover:shadow-lg'
              }`}
            >
              <Sparkles className="w-5 h-5" />
              <span>Run Evidence-Grounded Placement Analysis</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
