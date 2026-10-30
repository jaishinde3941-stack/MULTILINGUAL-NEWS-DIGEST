"use client";

import React, { useState, useEffect } from "react";
import { 
  X, ExternalLink, Volume2, VolumeX, Copy, Check, 
  Sparkles, MapPin, Tag, Globe, Clock, RefreshCw, AlertCircle, AlertTriangle, CheckCircle2 
} from "lucide-react";
import { Article, reprocessArticle } from "@/lib/api";

interface ArticleReaderModalProps {
  article: Article | null;
  onClose: () => void;
  onArticleUpdated?: (updated: Article) => void;
}

export const ArticleReaderModal: React.FC<ArticleReaderModalProps> = ({
  article,
  onClose,
  onArticleUpdated,
}) => {
  const [currentArticle, setCurrentArticle] = useState<Article | null>(article);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [reprocessError, setReprocessError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentArticle(article);
    setReprocessError(null);
  }, [article]);

  if (!currentArticle) return null;

  const getLanguageFlag = (lang: string) => {
    switch (lang?.toLowerCase()) {
      case "telugu":
      case "marathi":
      case "gujarati":
      case "hindi":
      case "tamil":
      case "malayalam":
        return "🇮🇳";
      case "french":
        return "🇫🇷";
      case "spanish":
        return "🇪🇸";
      case "german":
        return "🇩🇪";
      case "japanese":
        return "🇯🇵";
      case "arabic":
        return "🇸🇦";
      case "english":
        return "🇬🇧";
      default:
        return "🌐";
    }
  };

  const handleToggleSpeech = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      window.speechSynthesis.cancel();
      const textToRead = `${currentArticle.english_title}. ${currentArticle.english_summary}`;
      const utterance = new SpeechSynthesisUtterance(textToRead);
      utterance.lang = "en-US";
      utterance.rate = 1.0;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  const handleCopy = () => {
    const text = `${currentArticle.english_title}\n\nEnglish Executive Summary:\n${currentArticle.english_summary}\n\nSource: ${currentArticle.source_name} (${currentArticle.source_url})`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReprocess = async () => {
    setIsReprocessing(true);
    setReprocessError(null);
    try {
      const updated = await reprocessArticle(currentArticle.id);
      setCurrentArticle(updated);
      onArticleUpdated?.(updated);
    } catch (err: any) {
      setReprocessError(err.message || "Failed to reprocess with Llama 3.2");
    } finally {
      setIsReprocessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md transition-all">
      <div className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-2xl bg-[#0b1120] border border-slate-700/80 shadow-2xl overflow-hidden">
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between p-4 sm:px-6 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="px-3 py-1 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-300 text-xs font-bold">
              {currentArticle.source_name}
            </span>
            <span className="text-xs text-slate-300 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700">
              <span>{getLanguageFlag(currentArticle.original_language)}</span>
              <span>{currentArticle.original_language} → 🇬🇧 English</span>
            </span>
            <span className="text-xs text-slate-400 hidden md:inline-flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>{new Date(currentArticle.published_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Audio Reader */}
            <button
              onClick={handleToggleSpeech}
              title={isSpeaking ? "Stop Voice Reader" : "Listen to English Summary"}
              className={`p-2 rounded-lg border text-xs font-medium transition-all flex items-center gap-1.5 ${
                isSpeaking
                  ? "bg-rose-600 text-white border-rose-500"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700"
              }`}
            >
              {isSpeaking ? <VolumeX className="w-4 h-4 animate-pulse" /> : <Volume2 className="w-4 h-4 text-blue-400" />}
              <span className="hidden sm:inline">{isSpeaking ? "Stop" : "Listen"}</span>
            </button>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              title="Copy Summary & Translation"
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all cursor-pointer"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-slate-400" />}
            </button>

            {/* Source external link */}
            <a
              href={currentArticle.source_url}
              target="_blank"
              rel="noopener noreferrer"
              title="Visit original article on source site"
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
            >
              <ExternalLink className="w-4 h-4 text-slate-400" />
            </a>

            {/* Close Button */}
            <button
              onClick={() => {
                if (isSpeaking && typeof window !== "undefined") window.speechSynthesis.cancel();
                onClose();
              }}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Reader Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Article Header info */}
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-3 text-xs">
              <span className="px-2.5 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/30 text-blue-400 font-medium">
                {currentArticle.field}
              </span>
              <span className="flex items-center gap-1 text-slate-400">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <span>{currentArticle.region}</span>
                {currentArticle.subregion && <span>({currentArticle.subregion})</span>}
              </span>
              {currentArticle.processing_status === "failed" && (
                <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30 font-medium flex items-center gap-1 text-[11px]">
                  <AlertCircle className="w-3 h-3 text-rose-400" />
                  <span>Processing Failed</span>
                </span>
              )}
              {currentArticle.processing_status === "flagged" && (
                <span className="px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-300 border border-yellow-500/30 font-medium flex items-center gap-1 text-[11px]">
                  <AlertTriangle className="w-3 h-3 text-yellow-400" />
                  <span>Review Needed</span>
                </span>
              )}
            </div>

            <h1 className="text-xl sm:text-2xl md:text-3xl font-extrabold text-white leading-tight mb-2">
              {currentArticle.english_title}
            </h1>

            <p className="text-xs sm:text-sm text-slate-400 italic">
              Original {currentArticle.original_language} Headline: &quot;{currentArticle.original_title}&quot;
            </p>
          </div>

          {/* Reprocessing status / Error warning if failed */}
          {(currentArticle.processing_status === "failed" || currentArticle.processing_status === "flagged" || reprocessError) && (
            <div className="p-4 rounded-xl bg-slate-900/90 border border-amber-500/30 flex items-center justify-between gap-4">
              <div className="space-y-0.5">
                <p className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>AI Summarization Notice</span>
                </p>
                <p className="text-xs text-slate-400">
                  {reprocessError || currentArticle.processing_error || "This article may benefit from re-summarization with Llama 3.2."}
                </p>
              </div>
              <button
                onClick={handleReprocess}
                disabled={isReprocessing}
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors shrink-0 disabled:opacity-50 cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isReprocessing ? "animate-spin" : ""}`} />
                <span>{isReprocessing ? "Processing..." : "Re-summarize with Llama 3.2"}</span>
              </button>
            </div>
          )}

          {/* Single English Summary Section */}
          <div className="p-5 rounded-xl bg-gradient-to-br from-blue-950/40 via-slate-900/60 to-slate-900 border border-blue-500/30 shadow-md">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-blue-500/20">
              <div className="flex items-center gap-1.5 text-sm font-bold text-blue-400 uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>English Executive Summary</span>
              </div>
              <div className="flex items-center gap-2">
                {currentArticle.summary_word_count && currentArticle.summary_word_count > 0 ? (
                  <span className="text-xs text-slate-400">{currentArticle.summary_word_count} words</span>
                ) : null}
                <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1.5">
                  <span>🇬🇧</span>
                  <span>AI Summarized</span>
                </span>
              </div>
            </div>
            <div className="text-sm sm:text-base text-slate-200 leading-relaxed font-medium whitespace-pre-line space-y-4">
              {currentArticle.english_summary}
            </div>
          </div>

          {/* Verified Original Source Section (No raw RSS dump) */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-blue-400" />
                  <span>Original Publication Source</span>
                </span>
                <span className="text-[11px] px-2.5 py-0.5 rounded-md bg-blue-950/60 text-blue-300 border border-blue-500/30 font-semibold">
                  {currentArticle.source_name} ({currentArticle.original_language})
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Official dispatch from <span className="text-slate-300 font-medium">{currentArticle.region}</span> ({currentArticle.field}).
              </p>
              <p className="text-[11px] text-slate-500">
                Click below to read the complete, unabridged article directly at the publisher&apos;s site.
              </p>
            </div>

            <a
              href={currentArticle.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors shrink-0 shadow-md shadow-blue-950/50"
            >
              <span>Read Full Story on {currentArticle.source_name}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* Keywords & Tags Footer */}
          {currentArticle.keywords && currentArticle.keywords.length > 0 && (
            <div className="pt-4 border-t border-slate-800 flex items-center gap-2 flex-wrap text-xs">
              <div className="flex items-center gap-1 text-slate-400 font-semibold mr-1">
                <Tag className="w-3.5 h-3.5 text-slate-500" />
                <span>Extracted Entities:</span>
              </div>
              {currentArticle.keywords.map((kw, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 font-medium text-xs border border-slate-700/60"
                >
                  #{kw}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
