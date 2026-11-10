"use client";

import React, { useState, memo } from "react";
import { 
  Bookmark, ExternalLink, Flame, 
  Clock, MapPin, Languages, ArrowUpRight,
  AlertCircle, AlertTriangle,
  Tag
} from "lucide-react";
import { Article } from "@/lib/api";

interface ArticleCardProps {
  article: Article;
  onSelect: (article: Article) => void;
  onToggleBookmark: (id: number) => void;
  isAuthenticated: boolean;
  onFilterByRegion?: (region: string) => void;
  onFilterByLanguage?: (lang: string) => void;
  onFilterByField?: (field: string) => void;
  onFilterByKeyword?: (keyword: string) => void;
}

/**
 * Editorial neutral tag styling with subtle red accent for high-priority categories.
 */
export function getTagStyle(tag: string, field?: string): string {
  const lowerTag = tag.toLowerCase();
  const lowerField = (field || "").toLowerCase();

  // Breaking / Critical / Emergency (Editorial Red Accent)
  if (
    lowerTag.includes("emergency") ||
    lowerTag.includes("alert") ||
    lowerTag.includes("crisis") ||
    lowerTag.includes("breaking")
  ) {
    return "bg-[var(--accent-soft)] text-[var(--accent)] border-[var(--accent-border)]";
  }

  // Consistent Neutral Badge Styling
  return "bg-[var(--surface-secondary)] text-[var(--text-secondary)] border-[var(--border)] hover:border-[var(--text-muted)]";
}

const ArticleCardComponent: React.FC<ArticleCardProps> = ({
  article,
  onSelect,
  onToggleBookmark,
  isAuthenticated,
  onFilterByRegion,
  onFilterByLanguage,
  onFilterByField,
  onFilterByKeyword,
}) => {
  const [imgError, setImgError] = useState(false);
  const [imgLoaded, setImgLoaded] = useState(false);

  const getStatusBadge = () => {
    switch (article.processing_status) {
      case "pending":
        return (
          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/30 font-medium">
            Summarizing...
          </span>
        );
      case "failed":
        return (
          <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-700 dark:text-rose-300 border border-rose-500/30 font-medium flex items-center gap-1">
            <AlertCircle className="w-2.5 h-2.5" />
            <span>Summary Failed</span>
          </span>
        );
      case "flagged":
        return (
          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/30 font-medium flex items-center gap-1">
            <AlertTriangle className="w-2.5 h-2.5" />
            <span>Review Needed</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <article
      onClick={() => onSelect(article)}
      className="group relative flex flex-col justify-between rounded-xl bg-[var(--surface)] dark:bg-[var(--surface-secondary)] border border-[var(--border)] hover:border-[var(--border-hover)] hover:-translate-y-1 hover:shadow-md transition-[transform,box-shadow,border-color] duration-200 ease-out transform-gpu will-change-transform cursor-pointer overflow-hidden"
    >
      {/* 16:9 Image container without heavy decorative overlays */}
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-[var(--surface-secondary)] shrink-0 border-b border-[var(--border)]">
        {article.image_url && !imgError ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={article.image_url}
            alt={article.english_title}
            onError={() => setImgError(true)}
            onLoad={() => setImgLoaded(true)}
            className={`w-full h-full object-cover transition-[transform,opacity] duration-300 ease-out ${
              imgLoaded ? "opacity-100" : "opacity-0"
            } group-hover:scale-[1.02] transform-gpu will-change-transform`}
            loading="lazy"
            decoding="async"
          />
        ) : (
          <div className="w-full h-full bg-[var(--surface-secondary)] flex items-center justify-center">
            <Languages className="w-8 h-8 text-[var(--text-muted)] opacity-40" />
          </div>
        )}

        {/* Source and Original Language Badges */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 flex-wrap z-10">
          <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-[var(--surface)]/95 text-[var(--text-primary)] border border-[var(--border)] shadow-xs uppercase tracking-wider backdrop-blur-xs">
            {article.source_name}
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onFilterByLanguage?.(article.original_language);
            }}
            title={`Original Language: ${article.original_language}`}
            className="px-2 py-0.5 rounded text-[11px] font-medium bg-[var(--surface)]/90 hover:bg-[var(--surface)] text-[var(--text-secondary)] border border-[var(--border)] transition-colors cursor-pointer backdrop-blur-xs"
          >
            <span>From {article.original_language}</span>
          </button>
        </div>

        {/* Trending Indicator */}
        {article.trending && (
          <div className="absolute top-3 right-3 z-10">
            <span className="px-2.5 py-0.5 rounded bg-[var(--accent)] text-white text-[10px] font-semibold flex items-center gap-1 uppercase tracking-wider shadow-xs">
              <Flame className="w-3 h-3 text-white fill-white" />
              <span>Trending</span>
            </span>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Metadata Row: Category & Region (12px, Inter weight 500) */}
          <div className="flex items-center gap-2 flex-wrap text-[12px] font-medium mb-2.5">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFilterByField?.(article.field);
              }}
              className="text-[var(--accent)] uppercase tracking-wider hover:underline cursor-pointer"
            >
              {article.field}
            </button>
            <span className="text-[var(--border-hover)]">•</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFilterByRegion?.(article.region);
              }}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] flex items-center gap-1 cursor-pointer font-normal"
            >
              <MapPin className="w-3 h-3 text-[var(--text-muted)]" />
              <span>{article.region}</span>
              {article.subregion && <span className="text-[var(--text-muted)]">({article.subregion})</span>}
            </button>
            {getStatusBadge()}
          </div>

          {/* English Article Headline: 19-21px, weight 650-700, max 3 lines */}
          <h2 className="text-[19px] sm:text-[20px] font-bold text-[var(--text-primary)] leading-[1.3] group-hover:text-[var(--accent)] transition-colors mb-2.5 line-clamp-3">
            {article.english_title}
          </h2>

          {/* English Executive Summary: 14-15px, line-height ~1.6, line-clamp-3 */}
          <p className="text-[14px] sm:text-[14.5px] text-[var(--text-secondary)] leading-[1.6] line-clamp-3 mb-4 font-normal">
            {article.english_summary}
          </p>
        </div>

        {/* Footer Area: Tags & Actions */}
        <div>
          {/* Contextual Tags */}
          {article.keywords && article.keywords.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap mb-4">
              {article.keywords
                .filter((kw) => kw.toLowerCase() !== "states & regional" && kw.toLowerCase() !== "news")
                .slice(0, 3)
                .map((kw, i) => (
                  <button
                    key={`${kw}-${i}`}
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onFilterByKeyword?.(kw);
                    }}
                    title={`Filter by tag: ${kw}`}
                    className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border transition-colors cursor-pointer ${getTagStyle(kw, article.field)}`}
                  >
                    <Tag className="w-2.5 h-2.5 mr-1 opacity-70 shrink-0" />
                    <span>{kw}</span>
                  </button>
                ))}
            </div>
          )}

          {/* Bottom Metabar */}
          <div className="pt-3.5 border-t border-[var(--border)] flex items-center justify-between text-[12px] text-[var(--text-muted)]">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-[var(--text-muted)]" />
              {new Date(article.published_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })}
            </span>

            <div className="flex items-center gap-1.5">
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleBookmark(article.id);
                  }}
                  title={article.is_bookmarked ? "Remove Bookmark" : "Save Bookmark"}
                  className={`w-8 h-8 rounded-md border transition-colors cursor-pointer flex items-center justify-center ${
                    article.is_bookmarked
                      ? "bg-[var(--accent-soft)] border-[var(--accent)] text-[var(--accent)]"
                      : "bg-[var(--surface)] border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${article.is_bookmarked ? "fill-current" : ""}`} />
                </button>
              )}

              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                title="Visit original article source"
                className="w-8 h-8 rounded-md bg-[var(--surface)] border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:border-[var(--border-hover)] transition-colors flex items-center justify-center"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelect(article);
                }}
                className="flex items-center gap-1 h-8 px-2.5 rounded-md bg-[var(--surface)] hover:bg-[var(--surface-secondary)] border border-[var(--border)] text-[var(--text-primary)] font-medium transition-colors text-[12px] cursor-pointer active:scale-98"
              >
                <span>Read Full</span>
                <ArrowUpRight className="w-3 h-3 text-[var(--accent)]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
};

// Memoized ArticleCard prevents unnecessary re-renders
export const ArticleCard = memo(ArticleCardComponent, (prevProps, nextProps) => {
  return (
    prevProps.article.id === nextProps.article.id &&
    prevProps.article.is_bookmarked === nextProps.article.is_bookmarked &&
    prevProps.article.processing_status === nextProps.article.processing_status &&
    prevProps.article.english_title === nextProps.article.english_title &&
    prevProps.article.english_summary === nextProps.article.english_summary &&
    prevProps.isAuthenticated === nextProps.isAuthenticated &&
    prevProps.article.batch_id === nextProps.article.batch_id
  );
});
