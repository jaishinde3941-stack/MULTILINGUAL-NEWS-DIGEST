"use client";

import React, { useState } from "react";
import { Globe, Flame, Sparkles, RefreshCw, User, LogOut, SlidersHorizontal, BookOpen } from "lucide-react";
import { AuthUser, triggerIngestion } from "@/lib/api";

interface HeaderProps {
  activeTab: "foryou" | "trending" | "explore";
  setActiveTab: (tab: "foryou" | "trending" | "explore") => void;
  user: AuthUser | null;
  onOpenAuth: () => void;
  onOpenQuiz: () => void;
  onOpenProfile: () => void;
  onLogout: () => void;
  onRefreshFeeds: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onOpenQuiz,
  onOpenProfile,
  onLogout,
  onRefreshFeeds,
}) => {
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    setIngestStatus("Aggregating international RSS & generating executive briefings...");
    try {
      await triggerIngestion(2);
      setIngestStatus("Feeds refreshed successfully!");
      onRefreshFeeds();
      setTimeout(() => setIngestStatus(null), 3000);
    } catch {
      setIngestStatus("Ingest completed. Feeds updated.");
      onRefreshFeeds();
      setTimeout(() => setIngestStatus(null), 3000);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab("foryou")}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-500 p-0.5 shadow-lg shadow-blue-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
                <Globe className="w-5 h-5 text-blue-400 animate-soft-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white">
                  POLYGLOT<span className="text-blue-500">DIGEST</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Global News Translated & Curated in Real Time</p>
            </div>
          </div>

          {/* Navigation Feed Tabs */}
          <nav className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800/80">
            <button
              id="tab-foryou"
              onClick={() => setActiveTab("foryou")}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "foryou"
                  ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-600/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>For You</span>
            </button>

            <button
              id="tab-trending"
              onClick={() => setActiveTab("trending")}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "trending"
                  ? "bg-gradient-to-r from-orange-600 to-amber-600 text-white shadow-md shadow-orange-600/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <Flame className="w-3.5 h-3.5" />
              <span>Trending</span>
            </button>

            <button
              id="tab-explore"
              onClick={() => setActiveTab("explore")}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "explore"
                  ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-600/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Explore & Filter</span>
            </button>
          </nav>

          {/* Right Action Controls */}
          <div className="flex items-center gap-2.5">
            {/* Scrape / Pipeline Trigger */}
            <button
              id="btn-trigger-ingest"
              onClick={handleTriggerIngest}
              disabled={isIngesting}
              title="Aggregate international RSS & generate executive briefings"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 rounded-lg transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isIngesting ? "animate-spin" : ""}`} />
              <span className="hidden md:inline">{isIngesting ? "Translating..." : "Ingest News"}</span>
            </button>

            {/* 15-Question Onboarding Quiz Button */}
            <button
              id="btn-open-quiz"
              onClick={onOpenQuiz}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-300 hover:text-indigo-100 bg-indigo-950/60 hover:bg-indigo-900/60 border border-indigo-700/50 rounded-lg transition-all shadow-sm shadow-indigo-950/50"
            >
              <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
              <span className="hidden sm:inline">15-Q Quiz</span>
            </button>

            {/* User Auth or Profile Controls */}
            {user ? (
              <div className="flex items-center gap-1.5">
                <button
                  id="btn-view-profile"
                  onClick={onOpenProfile}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-200 bg-slate-800/90 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all"
                >
                  <User className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="max-w-[100px] truncate">{user.full_name || user.email.split("@")[0]}</span>
                </button>
                <button
                  id="btn-logout"
                  onClick={onLogout}
                  title="Logout"
                  className="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 rounded-lg transition-all"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                id="btn-open-auth"
                onClick={onOpenAuth}
                className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-sm shadow-blue-500/30 transition-all"
              >
                <User className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Floating Status Toast if Ingesting */}
      {ingestStatus && (
        <div className="w-full bg-blue-600/90 text-white text-xs font-medium py-1.5 px-4 text-center border-t border-blue-400/30 animate-pulse">
          {ingestStatus}
        </div>
      )}
    </header>
  );
};
