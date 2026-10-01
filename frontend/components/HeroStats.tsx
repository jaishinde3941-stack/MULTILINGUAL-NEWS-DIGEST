"use client";

import React from "react";
import { Globe2, ShieldCheck, Languages, CheckCircle2, FileText } from "lucide-react";
import { AuthUser } from "@/lib/api";

interface HeroStatsProps {
  user: AuthUser | null;
  onOpenQuiz: () => void;
  articleCount: number;
}

export const HeroStats: React.FC<HeroStatsProps> = ({ user, onOpenQuiz, articleCount }) => {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900/90 via-slate-900/40 to-slate-950 p-6 md:p-8 mb-8 shadow-2xl">
      {/* Background ambient lighting */}
      <div className="absolute top-0 right-1/4 w-96 h-48 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-80 h-40 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="max-w-2xl">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Global Intelligence Briefings in <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">Fluent English</span>
          </h1>

          <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed">
            Aggregates primary foreign journalism directly from leading international publications. 
            Articles are translated in real time, synthesized into crisp executive summaries, and organized 
            to eliminate language barriers—empowering you to absorb vital global developments with maximum efficiency.
          </p>

          {/* User Onboarding status banner */}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {user?.completed_onboarding ? (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-950/70 border border-emerald-500/30 text-emerald-300 text-xs font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Personalized Interest Graph Active (15 Dimensions Calibrated)</span>
                <button
                  onClick={onOpenQuiz}
                  className="underline hover:text-emerald-100 font-semibold ml-1 cursor-pointer"
                >
                  Adjust
                </button>
              </div>
            ) : user ? (
              <div className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30 text-indigo-200 text-xs font-medium">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span>Calibrate your &quot;For You&quot; feed with the 15-question strategic questionnaire.</span>
                <button
                  id="hero-quiz-cta"
                  onClick={onOpenQuiz}
                  className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold shadow-sm transition-all"
                >
                  Start Quiz
                </button>
              </div>
            ) : (
              <div className="inline-flex items-center gap-3 px-3.5 py-2 rounded-xl bg-slate-850/80 border border-slate-700/60 text-slate-300 text-xs font-medium">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
                <span>Guest Mode active: Trending news, filters, and reader are available. Sign in to unlock personalized ranking.</span>
              </div>
            )}
          </div>
        </div>

        {/* Real-time stats grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 shrink-0">
          <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Globe2 className="w-4 h-4 text-blue-400" />
              <span>Global Feeds</span>
            </div>
            <div className="text-xl font-bold text-white">Multi-Outlet</div>
            <div className="text-[11px] text-slate-400 mt-0.5">International Coverage</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Languages className="w-4 h-4 text-emerald-400" />
              <span>Languages</span>
            </div>
            <div className="text-xl font-bold text-white">Cross-Lingual</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Instant English Synthesis</div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-800/80 backdrop-blur-sm col-span-2 sm:col-span-1">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <FileText className="w-4 h-4 text-indigo-400" />
              <span>Executive Briefs</span>
            </div>
            <div className="text-xl font-bold text-white">{articleCount} Ingested</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Curated Dispatches</div>
          </div>
        </div>
      </div>
    </div>
  );
};
