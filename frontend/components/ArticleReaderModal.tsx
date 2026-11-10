"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { 
  X, ExternalLink, Volume2, VolumeX, Copy, Check, 
  MapPin, Clock, RefreshCw, AlertTriangle,
  ChevronDown
} from "lucide-react";
import { Article, reprocessArticle } from "@/lib/api";

interface ArticleReaderModalProps {
  article: Article | null;
  onClose: () => void;
  onArticleUpdated?: (updated: Article) => void;
}

/**
 * Normalizes and selects 2-4 high-value, English-only editorial contextual tags.
 * Deduplicates, filters generic filler, and formats as clean uppercase editorial tags.
 */
function getEditorialTags(article: Article): string[] {
  const genericTerms = new Set([
    "states & regional",
    "state & regional",
    "general news",
    "general",
    "news",
    "article",
    "update",
    "latest",
    "breaking",
    "report",
    "stories",
    "daily",
  ]);

  const candidates: string[] = [];

  // 1. Process existing article keywords
  if (Array.isArray(article.keywords)) {
    for (const kw of article.keywords) {
      if (typeof kw !== "string") continue;
      const trimmed = kw.trim();
      const lower = trimmed.toLowerCase();
      // Only English/ASCII characters allowed
      if (!/^[a-zA-Z0-9\s\-&'.]+$/.test(trimmed)) continue;
      // Skip generic boilerplate terms
      if (genericTerms.has(lower)) continue;
      // Skip strings that are overly long sentences or single characters
      if (trimmed.length > 25 || trimmed.length < 2) continue;
      // Deduplicate case-insensitively
      if (!candidates.some((c) => c.toLowerCase() === lower)) {
        candidates.push(trimmed.toUpperCase());
      }
    }
  }

  // 2. If fewer than 2 tags, supplement with meaningful editorial field
  if (candidates.length < 2 && article.field) {
    const fieldTag = article.field.trim().toUpperCase();
    if (
      !genericTerms.has(article.field.toLowerCase()) &&
      !candidates.some((c) => c === fieldTag)
    ) {
      candidates.unshift(fieldTag);
    }
  }

  // 3. If still fewer than 3 tags, infer topical editorial themes from English title
  if (candidates.length < 3 && article.english_title) {
    const titleUpper = article.english_title.toUpperCase();
    const topicKeywords = [
      { pattern: /\b(ELECTION|VOTE|POLL|CANDIDATE)\b/, tag: "ELECTION" },
      { pattern: /\b(ECONOMY|MARKET|FINANCE|TRADE|BUDGET|BANK|STOCK|RUPEE)\b/, tag: "ECONOMY" },
      { pattern: /\b(TECHNOLOGY|TECH|AI|DIGITAL|CYBER|SOFTWARE|SATELLITE|ISRO)\b/, tag: "TECHNOLOGY" },
      { pattern: /\b(DIPLOMACY|FOREIGN|GLOBAL|BILATERAL|TREATY|BORDER)\b/, tag: "DIPLOMACY" },
      { pattern: /\b(LEADERSHIP|MINISTER|GOVERNANCE|CABINET|POLICY|GOVERNMENT)\b/, tag: "LEADERSHIP" },
      { pattern: /\b(RAILWAY|TRANSIT|METRO|TRANSPORT|INFRASTRUCTURE|TRAIN)\b/, tag: "INFRASTRUCTURE" },
      { pattern: /\b(JUDICIARY|COURT|LEGAL|JUSTICE|VERDICT)\b/, tag: "JUDICIARY" },
      { pattern: /\b(HEALTH|MEDICAL|HOSPITAL|DISEASE|FOOD)\b/, tag: "HEALTHCARE" },
      { pattern: /\b(CLIMATE|ENVIRONMENT|WEATHER|MONSOON|RAIN)\b/, tag: "CLIMATE" },
    ];

    for (const item of topicKeywords) {
      if (item.pattern.test(titleUpper) && !candidates.includes(item.tag)) {
        candidates.push(item.tag);
        if (candidates.length >= 4) break;
      }
    }
  }

  // 4. Return between 2 and 4 tags
  return candidates.slice(0, 4);
}

export const ArticleReaderModal: React.FC<ArticleReaderModalProps> = ({
  article,
  onClose,
  onArticleUpdated,
}) => {
  const [localArticle, setLocalArticle] = useState<Article | null>(article);
  const [showOriginalHeadline, setShowOriginalHeadline] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [isReprocessing, setIsReprocessing] = useState<boolean>(false);
  const [reprocessError, setReprocessError] = useState<string | null>(null);

  // Sync internal state whenever the prop article changes or is cleared
  useEffect(() => {
    setLocalArticle(article);
    setReprocessError(null);
    setIsSpeaking(false);
    setShowOriginalHeadline(false);
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }, [article]);

  const handleClose = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
    onClose();
  }, [onClose]);

  // Handle Escape key & body scroll locking
  useEffect(() => {
    if (!article) return;

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        handleClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener("keydown", handleKeyDown);
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [article, handleClose]);

  const formattedDate = useMemo(() => {
    if (!localArticle?.published_at) return "";
    try {
      const d = new Date(localArticle.published_at);
      return isNaN(d.getTime())
        ? ""
        : d.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
          });
    } catch {
      return "";
    }
  }, [localArticle?.published_at]);

  const editorialTags = useMemo(() => {
    if (!localArticle) return [];
    return getEditorialTags(localArticle);
  }, [localArticle]);

  // If no article is active, render nothing (completely unmounted)
  if (!article || !localArticle) return null;

  const currentArticle = localArticle;

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
      setLocalArticle(updated);
      onArticleUpdated?.(updated);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to reprocess with Llama 3.2";
      setReprocessError(message);
    } finally {
      setIsReprocessing(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-[var(--modal-overlay)] backdrop-blur-md transition-all animate-modal-backdrop"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-article-title"
    >
      <div 
        className="relative w-full max-w-[850px] max-h-[85vh] flex flex-col rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-2xl overflow-hidden animate-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Compact Editorial Header */}
        <div className="flex items-center justify-between px-5 sm:px-6 py-3 border-b border-[var(--border)] bg-[var(--surface)] shrink-0 gap-3 select-none">
          {/* Metadata Byline: Publication name | Original language → English | Publication date */}
          <div className="flex items-center gap-2 sm:gap-2.5 flex-wrap min-w-0">
            <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--text-primary)]">
              {currentArticle.source_name}
            </span>
            <span className="text-[var(--border)] text-xs select-none">|</span>
            <span className="text-[12px] text-[var(--text-secondary)] font-normal inline-flex items-center gap-1.5">
              <span>{currentArticle.original_language}</span>
              <span className="text-[var(--text-muted)]">→</span>
              <span>English</span>
            </span>
            {formattedDate && (
              <>
                <span className="text-[var(--border)] text-xs select-none hidden sm:inline">|</span>
                <span className="text-[12px] text-[var(--text-muted)] font-normal hidden sm:inline-flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{formattedDate}</span>
                </span>
              </>
            )}
          </div>

          {/* Action Toolbar: Listen | Copy | Source | Close */}
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Listen Button */}
            <button
              type="button"
              onClick={handleToggleSpeech}
              title={isSpeaking ? "Stop Voice Reader" : "Listen to English Summary"}
              aria-label={isSpeaking ? "Stop Voice Reader" : "Listen to English Summary"}
              className={`h-8 px-2.5 rounded-md border text-[12px] font-medium transition-colors inline-flex items-center gap-1.5 cursor-pointer ${
                isSpeaking
                  ? "bg-[var(--accent)] text-white border-[var(--accent)]"
                  : "bg-[var(--surface)] hover:bg-[var(--surface-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border-[var(--border)]"
              }`}
            >
              {isSpeaking ? (
                <VolumeX className="w-3.5 h-3.5 animate-pulse" />
              ) : (
                <Volume2 className="w-3.5 h-3.5 text-[var(--accent)]" />
              )}
              <span className="hidden sm:inline">{isSpeaking ? "Stop" : "Listen"}</span>
            </button>

            {/* Copy Button */}
            <button
              type="button"
              onClick={handleCopy}
              title="Copy Summary to clipboard"
              aria-label="Copy summary to clipboard"
              className="h-8 px-2.5 rounded-md bg-[var(--surface)] hover:bg-[var(--surface-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border)] transition-colors inline-flex items-center gap-1.5 cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span className="hidden sm:inline text-emerald-600 dark:text-emerald-400 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Copy</span>
                </>
              )}
            </button>

            {/* Open Original Article Button */}
            <a
              href={currentArticle.source_url}
              target="_blank"
              rel="noopener noreferrer"
              title="Open original article on publisher's website"
              aria-label="Open original article on publisher's website"
              className="h-8 px-2.5 rounded-md bg-[var(--surface)] hover:bg-[var(--surface-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border)] transition-colors inline-flex items-center gap-1.5"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Source</span>
            </a>

            {/* Close Button */}
            <button
              id="btn-close-reader-modal"
              type="button"
              onClick={handleClose}
              title="Close article (Esc)"
              aria-label="Close article"
              className="w-8 h-8 rounded-md bg-[var(--surface)] hover:bg-[var(--surface-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border)] transition-colors inline-flex items-center justify-center cursor-pointer active:scale-95"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Editorial Content Body */}
        <div className="px-6 sm:px-8 py-5 sm:py-7 overflow-y-auto flex-1">
          {/* Subtle Metadata Kicker: Editorial category & Region */}
          <div className="flex items-center gap-2 flex-wrap text-[12px] tracking-wider uppercase mb-2">
            <span className="text-[var(--accent)] font-semibold">
              {currentArticle.field || "General News"}
            </span>
            <span className="text-[var(--border-hover)]">•</span>
            <span className="flex items-center gap-1 text-[var(--text-secondary)] font-normal">
              <MapPin className="w-3.5 h-3.5 text-[var(--text-muted)]" />
              <span>{currentArticle.region}</span>
              {currentArticle.subregion && (
                <span className="text-[var(--text-muted)]">({currentArticle.subregion})</span>
              )}
            </span>
          </div>

          {/* Prominent English Headline in Newsreader: 36-40px desktop, weight 650 */}
          <h1 
            id="modal-article-title"
            className="font-editorial text-2xl sm:text-3xl md:text-[36px] lg:text-[40px] font-semibold text-[var(--text-primary)] leading-[1.2] tracking-tight mb-2.5"
          >
            {currentArticle.english_title}
          </h1>

          {/* Original-language headline below it in smaller muted italic text */}
          {currentArticle.original_title && (
            <div className="mb-6">
              <button
                type="button"
                onClick={() => setShowOriginalHeadline((prev) => !prev)}
                className="inline-flex items-center gap-1.5 text-[12px] font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors cursor-pointer select-none py-1 group focus:outline-none"
                aria-expanded={showOriginalHeadline}
              >
                <ChevronDown
                  className={`w-3.5 h-3.5 text-[var(--text-muted)] transition-transform duration-200 ${
                    showOriginalHeadline ? "rotate-180 text-[var(--accent)]" : "group-hover:translate-y-0.5"
                  }`}
                />
                <span>
                  {showOriginalHeadline
                    ? `Hide Original Headline (${currentArticle.original_language})`
                    : `View Original Headline (${currentArticle.original_language})`}
                </span>
              </button>

              {showOriginalHeadline && (
                <div className="mt-2 pl-3 py-1.5 border-l-2 border-[var(--accent-border)] text-[13px] sm:text-[14px] text-[var(--text-muted)] italic font-normal leading-relaxed animate-modal-backdrop">
                  &ldquo;{currentArticle.original_title}&rdquo;
                </div>
              )}
            </div>
          )}

          {/* Reprocessing status / Error warning if failed */}
          {(currentArticle.processing_status === "failed" || currentArticle.processing_status === "flagged" || reprocessError) && (
            <div className="p-3.5 rounded-lg bg-[var(--surface-secondary)] border border-[var(--border)] flex items-center justify-between gap-4 my-4">
              <div className="space-y-0.5">
                <p className="text-xs font-semibold text-[var(--accent)] flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  <span>AI Summarization Notice</span>
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  {reprocessError || currentArticle.processing_error || "This article may benefit from re-summarization with Llama 3.2."}
                </p>
              </div>
              <button
                type="button"
                onClick={handleReprocess}
                disabled={isReprocessing}
                className="px-3 py-1.5 rounded-md bg-[var(--surface)] hover:bg-[var(--surface-secondary)] text-[var(--text-primary)] border border-[var(--border)] font-medium text-xs flex items-center gap-1.5 transition-colors shrink-0 disabled:opacity-50 cursor-pointer shadow-xs"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isReprocessing ? "animate-spin" : ""}`} />
                <span>{isReprocessing ? "Processing..." : "Re-summarize"}</span>
              </button>
            </div>
          )}

          {/* Distinct ENGLISH EXECUTIVE SUMMARY Section: Inter 17px, line-height 1.75 */}
          <div className="my-6">
            <div className="flex items-center justify-between border-b border-[var(--border)] pb-2 mb-4">
              <h2 className="text-[12px] font-bold uppercase tracking-widest text-[var(--text-secondary)]">
                ENGLISH EXECUTIVE SUMMARY
              </h2>
              {currentArticle.summary_word_count && currentArticle.summary_word_count > 0 ? (
                <span className="text-[11px] font-medium text-[var(--text-muted)]">
                  {currentArticle.summary_word_count} words
                </span>
              ) : null}
            </div>

            <div className="text-[16px] sm:text-[17px] text-[var(--text-primary)] leading-[1.75] font-normal max-w-prose space-y-4">
              {currentArticle.english_summary.split(/\n\s*\n/).map((paragraph, index) => (
                <p key={index}>{paragraph.trim()}</p>
              ))}
            </div>
          </div>

          {/* Separate SOURCE SECTION with Read Full Story button */}
          <div className="pt-5 mt-6 border-t border-[var(--border)] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[12px]">
            <div className="text-[var(--text-muted)] font-normal flex items-center flex-wrap gap-x-2 gap-y-1">
              <span>Original source:</span>
              <span className="font-semibold text-[var(--text-primary)]">{currentArticle.source_name}</span>
              <span className="text-[var(--border-hover)]">•</span>
              <span>{currentArticle.original_language}</span>
              {currentArticle.region && (
                <>
                  <span className="text-[var(--border-hover)]">•</span>
                  <span>{currentArticle.region}</span>
                </>
              )}
            </div>

            <a
              href={currentArticle.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="h-8 px-3 rounded-lg bg-[var(--surface-secondary)] hover:bg-[var(--accent-soft)] border border-[var(--border)] hover:border-[var(--accent-border)] text-[var(--text-primary)] hover:text-[var(--accent)] font-medium text-[12px] transition-colors inline-flex items-center gap-1.5 shrink-0 group cursor-pointer"
              title={`Read full story on ${currentArticle.source_name}`}
            >
              <span>Read Full Story</span>
              <ExternalLink className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </a>
          </div>

          {/* Contextual Tags */}
          {editorialTags.length >= 2 && (
            <div className="pt-4 mt-2 flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-bold tracking-widest uppercase text-[var(--text-muted)] mr-1">
                Tags:
              </span>
              {editorialTags.map((tag, idx) => {
                const isAccent = idx === 0;
                return (
                  <span
                    key={tag}
                    className={`inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-semibold tracking-wider uppercase transition-colors ${
                      isAccent
                        ? "bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent-border)]"
                        : "bg-[var(--surface-secondary)] text-[var(--text-secondary)] border border-[var(--border)]"
                    }`}
                  >
                    {tag}
                  </span>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
