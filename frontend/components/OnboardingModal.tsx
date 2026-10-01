"use client";

import React, { useState, useEffect } from "react";
import { 
  X, ChevronLeft, ChevronRight, CheckCircle, Sparkles, 
  Compass, Cpu, Languages, Check, ArrowRight, Lock, AlertCircle 
} from "lucide-react";
import { 
  fetchOnboardingQuestions, 
  submitOnboarding, 
  QuizQuestion, 
  UserProfile 
} from "@/lib/api";

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (profile: UserProfile) => void;
  isAuthenticated?: boolean;
  onRequireAuth?: () => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  isAuthenticated = false,
  onRequireAuth,
}) => {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string[]>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [completedProfile, setCompletedProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadQuestions();
      setErrorMessage(null);
    }
  }, [isOpen]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const data = await fetchOnboardingQuestions();
      setQuestions(data.questions);
      // Pre-select first options if empty
      const initial: Record<number, string[]> = {};
      data.questions.forEach((q) => {
        initial[q.id] = [q.options[0].id];
      });
      setAnswers(initial);
    } catch (err) {
      console.error("Failed to load questions", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentQ = questions[currentIndex];
  const progressPercent = questions.length > 0 ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

  const handleSelectOption = (optionId: string) => {
    if (!currentQ) return;
    setAnswers((prev) => ({
      ...prev,
      [currentQ.id]: [optionId],
    }));
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setErrorMessage(null);

    // If not authenticated, prompt login/registration to save profile
    if (!isAuthenticated) {
      setErrorMessage("Please sign in or create an account to save your quiz answers and unlock match percentages.");
      if (onRequireAuth) {
        onRequireAuth();
      }
      return;
    }

    setSubmitting(true);
    try {
      const payload = Object.entries(answers).map(([qId, optIds]) => ({
        question_id: parseInt(qId, 10),
        selected_option_ids: optIds,
      }));
      const profile = await submitOnboarding(payload);
      setCompletedProfile(profile);
      onComplete(profile);
    } catch (err: unknown) {
      console.error("Failed to submit onboarding", err);
      if (err instanceof Error) {
        setErrorMessage(err.message || "Failed to submit onboarding answers. Please make sure you are signed in.");
      } else {
        setErrorMessage("Please sign in or create an account to save your interest graph.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getDimensionBadge = (dimension: string) => {
    switch (dimension) {
      case "region":
        return { label: "Geographic Focus", icon: Compass, color: "text-blue-400 bg-blue-500/10 border-blue-500/30" };
      case "field":
        return { label: "Topical Domain", icon: Cpu, color: "text-purple-400 bg-purple-500/10 border-purple-500/30" };
      case "language":
        return { label: "Language & Style", icon: Languages, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" };
      default:
        return { label: "General", icon: Sparkles, color: "text-slate-400 bg-slate-500/10 border-slate-500/30" };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-all">
      <div className="relative w-full max-w-2xl overflow-hidden rounded-2xl bg-[#0d1424] border border-slate-700/80 shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header / Progress bar */}
        <div className="border-b border-slate-800 p-5 pb-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
              <span className="text-xs font-bold tracking-wider text-slate-300 uppercase">
                15-Question Interest Graph Calibration
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Guest notification notice */}
          {!isAuthenticated && (
            <div className="mb-2.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <span>Guest Mode: Sign in to save answers and unlock match % badges.</span>
              </div>
              {onRequireAuth && (
                <button
                  type="button"
                  onClick={onRequireAuth}
                  className="font-bold underline hover:text-amber-200 ml-2 cursor-pointer"
                >
                  Sign In
                </button>
              )}
            </div>
          )}

          {/* Progress track */}
          {!completedProfile && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 font-medium mb-1.5">
                <span>Question {currentIndex + 1} of {questions.length}</span>
                <span className="font-semibold text-blue-400">{progressPercent}% Completed</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Error notification */}
        {errorMessage && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            {!isAuthenticated && onRequireAuth && (
              <button
                type="button"
                onClick={onRequireAuth}
                className="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-bold transition-all cursor-pointer"
              >
                Sign In Now
              </button>
            )}
          </div>
        )}

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-slate-400">Loading 15 interest calibration questions...</p>
            </div>
          ) : completedProfile ? (
            /* Celebration / Interest Graph Summary Screen */
            <div className="text-center py-8 px-4 animate-in fade-in duration-300">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/10">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Interest Graph Calibrated!</h2>
              <p className="text-sm text-slate-300 max-w-md mx-auto mb-6 leading-relaxed">
                Your 15 questions have been mapped into real-time interest weights. Your &quot;For You&quot; feed and filtered intelligence dispatches now display live <strong className="text-indigo-300 font-bold">% Match</strong> affinity scores.
              </p>

              {/* Preferences Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left mb-6">
                <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider block mb-1">
                    Top Regions
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {completedProfile.preferred_regions.length > 0 ? (
                      completedProfile.preferred_regions.slice(0, 3).map((r) => (
                        <span key={r} className="px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-300 text-xs font-medium">
                          {r}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">Regional Focus</span>
                    )}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[11px] font-semibold text-purple-400 uppercase tracking-wider block mb-1">
                    Top Fields
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {completedProfile.preferred_fields.length > 0 ? (
                      completedProfile.preferred_fields.slice(0, 3).map((f) => (
                        <span key={f} className="px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 text-xs font-medium">
                          {f}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">Politics & Tech</span>
                    )}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                  <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                    Languages
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {completedProfile.preferred_languages.length > 0 ? (
                      completedProfile.preferred_languages.slice(0, 3).map((l) => (
                        <span key={l} className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 text-xs font-medium">
                          {l}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">Multilingual</span>
                    )}
                  </div>
                </div>
              </div>

              <button
                id="btn-close-onboarding-success"
                onClick={onClose}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-500/30 transition-all cursor-pointer"
              >
                <span>Launch My Personalized Feed</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : currentQ ? (
            /* Current Question Card */
            <div>
              {/* Question Dimension Pill */}
              {(() => {
                const badge = getDimensionBadge(currentQ.dimension);
                const Icon = badge.icon;
                return (
                  <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-semibold mb-3 ${badge.color}`}>
                    <Icon className="w-3.5 h-3.5" />
                    <span>{badge.label}</span>
                  </div>
                );
              })()}

              <h3 className="text-xl font-bold text-white mb-1.5">{currentQ.title}</h3>
              <p className="text-sm text-slate-400 mb-6">{currentQ.subtitle}</p>

              {/* Options List */}
              <div className="space-y-2.5">
                {currentQ.options.map((opt) => {
                  const isSelected = (answers[currentQ.id] || []).includes(opt.id);
                  return (
                    <div
                      key={opt.id}
                      onClick={() => handleSelectOption(opt.id)}
                      className={`cursor-pointer p-4 rounded-xl border transition-all flex items-start justify-between gap-3 ${
                        isSelected
                          ? "bg-gradient-to-r from-blue-950/70 to-indigo-950/70 border-blue-500 text-white shadow-md shadow-blue-950/40"
                          : "bg-slate-800/40 border-slate-700/60 hover:bg-slate-800/80 hover:border-slate-600 text-slate-300"
                      }`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-sm">{opt.label}</span>
                        </div>
                        {opt.description && (
                          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                            {opt.description}
                          </p>
                        )}
                      </div>

                      <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                        isSelected ? "border-blue-400 bg-blue-500 text-white" : "border-slate-600 bg-slate-900"
                      }`}>
                        {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer Navigation Buttons */}
        {!completedProfile && (
          <div className="border-t border-slate-800 p-4 bg-slate-950/60 flex items-center justify-between">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0 || submitting}
              className={`flex items-center gap-1 px-4 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                currentIndex === 0 || submitting
                  ? "opacity-40 border-slate-800 text-slate-600 cursor-not-allowed"
                  : "border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              id="quiz-next-btn"
              onClick={handleNext}
              disabled={submitting}
              className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/30 transition-all cursor-pointer"
            >
              <span>{currentIndex === questions.length - 1 ? (submitting ? "Analyzing Graph..." : "Finish & Save") : "Continue"}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
