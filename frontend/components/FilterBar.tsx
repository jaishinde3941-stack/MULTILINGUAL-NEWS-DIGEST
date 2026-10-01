"use client";

import React from "react";
import { Search, X, RotateCcw, Filter, MapPin, Languages, BookOpen } from "lucide-react";
import { FilterMetadata } from "@/lib/api";

interface FilterBarProps {
  metadata: FilterMetadata;
  selectedRegion: string;
  setSelectedRegion: (region: string) => void;
  selectedLanguage: string;
  setSelectedLanguage: (lang: string) => void;
  selectedField: string;
  setSelectedField: (field: string) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onResetFilters: () => void;
  totalResults: number;
}

const DEFAULT_REGIONS = [
  "Gujarat",
  "India",
  "Kerala",
  "Maharashtra",
  "Tamil Nadu",
  "Telangana/Andhra Pradesh"
];

const DEFAULT_LANGUAGES = [
  "Gujarati",
  "Hindi",
  "Malayalam",
  "Marathi",
  "Tamil",
  "Telugu"
];

const DEFAULT_FIELDS = [
  "Agriculture & Rural",
  "Culture & Society",
  "Education & Jobs",
  "Entertainment & Cinema",
  "Finance & Economics",
  "Health & Wellness",
  "Politics",
  "States & Regional",
  "Technology & AI"
];

export const FilterBar: React.FC<FilterBarProps> = ({
  metadata,
  selectedRegion,
  setSelectedRegion,
  selectedLanguage,
  setSelectedLanguage,
  selectedField,
  setSelectedField,
  searchQuery,
  setSearchQuery,
  onResetFilters,
  totalResults,
}) => {
  const regions = metadata.regions && metadata.regions.length > 0 ? metadata.regions : DEFAULT_REGIONS;
  const languages = metadata.languages && metadata.languages.length > 0 ? metadata.languages : DEFAULT_LANGUAGES;
  const fields = metadata.fields && metadata.fields.length > 0 ? metadata.fields : DEFAULT_FIELDS;

  const isFiltered =
    selectedRegion !== "All" ||
    selectedLanguage !== "All" ||
    selectedField !== "All" ||
    searchQuery.trim().length > 0;

  return (
    <div className="bg-[#0f172a]/90 border border-slate-800 rounded-2xl p-4 sm:p-5 mb-8 backdrop-blur-xl shadow-lg">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            id="input-article-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search headlines, keywords, tags, or topics..."
            className="w-full pl-10 pr-9 py-2 text-xs sm:text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Results Counter & Reset */}
        <div className="flex items-center justify-between md:justify-end gap-3 text-xs text-slate-400 shrink-0">
          <span className="font-medium">
            Showing <strong className="text-white font-bold">{totalResults}</strong> articles
          </span>
          {isFiltered && (
            <button
              id="btn-reset-filters"
              onClick={onResetFilters}
              className="flex items-center gap-1 px-2.5 py-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-all cursor-pointer"
            >
              <RotateCcw className="w-3 h-3 text-blue-400" />
              <span>Reset Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Dropdown Filters Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Region Filter */}
        <div>
          <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            <MapPin className="w-3 h-3 text-blue-400" />
            <span>Region</span>
          </label>
          <select
            id="select-region"
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            <option value="All">All Global Regions</option>
            {regions.map((reg) => (
              <option key={reg} value={reg}>
                {reg}
              </option>
            ))}
          </select>
        </div>

        {/* Original Language Filter */}
        <div>
          <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            <Languages className="w-3 h-3 text-emerald-400" />
            <span>Original Language</span>
          </label>
          <select
            id="select-language"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            <option value="All">All Source Languages</option>
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </div>

        {/* Field / Topic Filter */}
        <div>
          <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            <BookOpen className="w-3 h-3 text-indigo-400" />
            <span>Editorial Field</span>
          </label>
          <select
            id="select-field"
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="w-full px-3 py-2 text-xs sm:text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            <option value="All">All Editorial Topics</option>
            {fields.map((field) => (
              <option key={field} value={field}>
                {field}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Active Filter Chips */}
      {isFiltered && (
        <div className="mt-3.5 pt-3 border-t border-slate-800/80 flex items-center gap-2 flex-wrap text-xs">
          <span className="text-slate-400 text-[11px] flex items-center gap-1">
            <Filter className="w-3 h-3 text-blue-400" />
            <span>Active:</span>
          </span>

          {selectedRegion !== "All" && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-950/80 border border-blue-500/40 text-blue-300 text-[11px]">
              <span>Region: {selectedRegion}</span>
              <button
                type="button"
                onClick={() => setSelectedRegion("All")}
                className="hover:text-white cursor-pointer ml-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {selectedLanguage !== "All" && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-[11px]">
              <span>Language: {selectedLanguage}</span>
              <button
                type="button"
                onClick={() => setSelectedLanguage("All")}
                className="hover:text-white cursor-pointer ml-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {selectedField !== "All" && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-950/80 border border-purple-500/40 text-purple-300 text-[11px]">
              <span>Field: {selectedField}</span>
              <button
                type="button"
                onClick={() => setSelectedField("All")}
                className="hover:text-white cursor-pointer ml-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {searchQuery.trim() && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-300 text-[11px]">
              <span>Search: &quot;{searchQuery.trim()}&quot;</span>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="hover:text-white cursor-pointer ml-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
};
