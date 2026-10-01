"use client";

import React from "react";
import { 
  Bookmark, ExternalLink, Sparkles, Flame, 
  Clock, MapPin, Languages, ArrowUpRight 
} from "lucide-react";
import { Article } from "@/lib/api";

interface ArticleCardProps {
  article: Article;
  onSelect: (article: Article) => void;
  onToggleBookmark: (id: number) => void;
  isAuthenticated: boolean;
  hasCompletedQuiz?: boolean;
  onFilterByRegion?: (region: string) => void;
  onFilterByLanguage?: (lang: string) => void;
  onFilterByField?: (field: string) => void;
  onFilterByKeyword?: (keyword: string) => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onSelect,
  onToggleBookmark,
  isAuthenticated,
  hasCompletedQuiz = false,
  onFilterByRegion,
  onFilterByLanguage,
  onFilterByField,
  onFilterByKeyword,
}) => {
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

  const getFieldColor = (field: string) => {
    switch (field) {
      case "Politics":
        return "text-purple-400 bg-purple-500/10 border-purple-500/30 hover:bg-purple-500/20";
      case "Technology & AI":
        return "text-cyan-400 bg-cyan-500/10 border-cyan-500/30 hover:bg-cyan-500/20";
      case "Education & Jobs":
        return "text-sky-400 bg-sky-500/10 border-sky-500/30 hover:bg-sky-500/20";
      case "Entertainment & Cinema":
        return "text-amber-400 bg-amber-500/10 border-amber-500/30 hover:bg-amber-500/20";
      case "Health & Wellness":
        return "text-rose-400 bg-rose-500/10 border-rose-500/30 hover:bg-rose-500/20";
      case "Agriculture & Rural":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30 hover:bg-emerald-500/20";
      case "Finance & Economics":
        return "text-teal-400 bg-teal-500/10 border-teal-500/30 hover:bg-teal-500/20";
      case "Culture & Society":
        return "text-pink-400 bg-pink-500/10 border-pink-500/30 hover:bg-pink-500/20";
      case "States & Regional":
        return "text-indigo-400 bg-indigo-500/10 border-indigo-500/30 hover:bg-indigo-500/20";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/30 hover:bg-slate-500/20";
    }
  };

  const matchPercent = typeof article.match_score === "number" && article.match_score > 0
    ? Math.round(article.match_score * 100)
    : null;

  return (
    <article className="group relative flex flex-col justify-between overflow-hidden rounded-2xl bg-[#0f172a]/70 border border-slate-800/80 hover:border-slate-700 hover:bg-[#131d36]/80 transition-all duration-300 shadow-lg hover:shadow-2xl">
      {/* Top Media / Thumbnail */}
      <div className="relative h-48 w-full overflow-hidden bg-slate-900">
        {article.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={article.image_url}
            alt={article.english_title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-tr from-slate-900 via-indigo-950/40 to-slate-900 flex items-center justify-center">
            <Languages className="w-10 h-10 text-slate-700" />
          </div>
        )}

        <div className="absolute inset-0 bg-gradient-to-t from-[#0f172a] via-transparent to-black/30" />

        {/* Source & Translation Pill */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 flex-wrap">
          <span className="px-2.5 py-1 rounded-lg bg-black/70 backdrop-blur-md border border-white/10 text-white font-bold text-xs shadow-sm">
            {article.source_name}
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onFilterByLanguage?.(article.original_language);
            }}
            title={`Filter articles by language: ${article.original_language}`}
            className="px-2 py-0.5 rounded-lg bg-blue-950/80 hover:bg-blue-900 backdrop-blur-md border border-blue-500/30 text-blue-300 text-[11px] font-semibold flex items-center gap-1 transition-colors cursor-pointer"
          >
            <span>{getLanguageFlag(article.original_language)}</span>
            <span>From {article.original_language}</span>
          </button>
        </div>

        {/* Trending or Personalization Badge */}
        <div className="absolute top-3 right-3 flex items-center gap-1">
          {article.trending && (
            <span className="px-2 py-0.5 rounded-lg bg-orange-600/90 backdrop-blur-md text-white text-[11px] font-bold flex items-center gap-1 shadow-md shadow-orange-950/50">
              <Flame className="w-3 h-3 text-amber-200 fill-amber-200" />
              <span>Trending</span>
            </span>
          )}
          {/* Strictly only show match percent if logged in AND completed onboarding quiz */}
          {isAuthenticated && hasCompletedQuiz && matchPercent !== null && (
            <span
              id={`badge-match-${article.id}`}
              title={`Personalized recommendation: ${matchPercent}% affinity based on your 15-question interest graph`}
              className="px-2.5 py-0.5 rounded-lg bg-indigo-600/90 backdrop-blur-md text-white text-[11px] font-bold flex items-center gap-1 shadow-md shadow-indigo-950/50 animate-soft-pulse"
            >
              <Sparkles className="w-3 h-3 text-indigo-200" />
              <span>{matchPercent}% Match</span>
            </span>
          )}
        </div>
      </div>

      {/* Content Area - Guaranteed English Display */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Metadata tags */}
          <div className="flex items-center gap-2 flex-wrap text-[11px] mb-2.5">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFilterByField?.(article.field);
              }}
              title={`Filter by field: ${article.field}`}
              className={`px-2 py-0.5 rounded-md border font-medium transition-colors cursor-pointer ${getFieldColor(article.field)}`}
            >
              {article.field}
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFilterByRegion?.(article.region);
              }}
              title={`Filter by region: ${article.region}`}
              className="inline-flex items-center gap-1 text-slate-400 hover:text-white px-1.5 py-0.5 rounded bg-slate-800/40 hover:bg-slate-800 border border-slate-700/50 transition-colors cursor-pointer"
            >
              <MapPin className="w-3 h-3 text-slate-500" />
              <span>{article.region}</span>
              {article.subregion && <span className="text-slate-500">• {article.subregion}</span>}
            </button>
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
              English Edition
            </span>
          </div>

          {/* Guaranteed English Title */}
          <h2
            onClick={() => onSelect(article)}
            className="text-base sm:text-lg font-bold text-white group-hover:text-blue-400 transition-colors cursor-pointer leading-snug mb-3 line-clamp-2"
          >
            {article.english_title}
          </h2>

          {/* AI Executive Summary Bullets (in English) */}
          <div className="bg-slate-900/60 rounded-xl p-3.5 border border-slate-800/80 mb-4">
            <div className="flex items-center gap-1.5 text-[10px] font-semibold text-blue-400 uppercase tracking-wider mb-2">
              <Sparkles className="w-3 h-3 text-blue-400" />
              <span>Executive Summary</span>
            </div>
            <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
              {article.english_summary.split("\n").map((line, idx) => (
                <p key={idx} className="line-clamp-2">
                  {line}
                </p>
              ))}
            </div>
          </div>
        </div>

        {/* Footer info & Actions */}
        <div>
          {/* Keywords / Tags */}
          {article.keywords && article.keywords.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap mb-4">
              {article.keywords.slice(0, 4).map((kw, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onFilterByKeyword?.(kw);
                  }}
                  title={`Filter articles matching tag: ${kw}`}
                  className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800/90 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60 transition-colors cursor-pointer"
                >
                  #{kw}
                </button>
              ))}
            </div>
          )}

          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1 text-[11px]">
              <Clock className="w-3 h-3 text-slate-500" />
              {new Date(article.published_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })}
            </span>

            <div className="flex items-center gap-2">
              {isAuthenticated && (
                <button
                  onClick={() => onToggleBookmark(article.id)}
                  title={article.is_bookmarked ? "Remove Bookmark" : "Save Bookmark"}
                  className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
                    article.is_bookmarked
                      ? "bg-blue-600/20 border-blue-500 text-blue-400"
                      : "bg-slate-800/80 border-slate-700/60 text-slate-400 hover:text-white"
                  }`}
                >
                  <Bookmark className={`w-3.5 h-3.5 ${article.is_bookmarked ? "fill-blue-400" : ""}`} />
                </button>
              )}

              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                title="View original article link"
                className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <button
                onClick={() => onSelect(article)}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 border border-blue-500/40 text-blue-300 hover:text-white font-semibold transition-all text-xs cursor-pointer"
              >
                <span>Read Full</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
};
