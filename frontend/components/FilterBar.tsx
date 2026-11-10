"use client";

import React from "react";
import { Search, X, RotateCcw, ChevronDown } from "lucide-react";
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
  searchInputRef?: React.RefObject<HTMLInputElement | null>;
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
  searchInputRef,
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
    <div className="bg-[var(--surface)] dark:bg-[var(--surface-secondary)] border border-[var(--border)] rounded-xl p-[18px] sm:p-5 mb-8 transition-colors duration-200">
      {/* First Row: Search input + article count & reset */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
        {/* Search input occupying most width */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            ref={searchInputRef}
            id="input-article-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search headlines, keywords, tags, or topics in English..."
            className="w-full h-[42px] pl-10 pr-10 text-[14px] bg-[var(--input-background)] border border-[var(--border)] rounded-lg text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] transition-colors"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              aria-label="Clear search query"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)] cursor-pointer p-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Article count aligned to the right + optional reset */}
        <div className="flex items-center justify-between md:justify-end gap-3 text-[13px] text-[var(--text-secondary)] shrink-0">
          <span className="font-normal">
            Showing <strong className="text-[var(--text-primary)] font-semibold">{totalResults}</strong> articles
          </span>
          {isFiltered && (
            <button
              id="btn-reset-filters"
              type="button"
              onClick={onResetFilters}
              className="flex items-center gap-1.5 px-2.5 py-1 text-[12px] font-medium text-[var(--accent)] hover:bg-[var(--accent-soft)] rounded-md border border-[var(--border)] transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Second Row: Three equally sized filter controls */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* 1. REGION */}
        <div>
          <label 
            htmlFor="select-region"
            className="block text-[12px] font-medium uppercase tracking-wider text-[var(--text-secondary)] mb-1.5"
          >
            REGION
          </label>
          <div className="relative">
            <select
              id="select-region"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full h-[40px] pl-3.5 pr-9 text-[13px] sm:text-[14px] bg-[var(--input-background)] border border-[var(--border)] hover:border-[var(--border-hover)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/15 focus:border-[var(--accent)] cursor-pointer transition-all appearance-none"
            >
              <option value="All">All Global Regions</option>
              {regions.map((reg) => (
                <option key={reg} value={reg}>
                  {reg}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-[var(--text-muted)] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none transition-transform" />
          </div>
        </div>

        {/* 2. ORIGINAL LANGUAGE */}
        <div>
          <label 
            htmlFor="select-language"
            className="block text-[12px] font-medium uppercase tracking-wider text-[var(--text-secondary)] mb-1.5"
          >
            ORIGINAL LANGUAGE
          </label>
          <div className="relative">
            <select
              id="select-language"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full h-[40px] pl-3.5 pr-9 text-[13px] sm:text-[14px] bg-[var(--input-background)] border border-[var(--border)] hover:border-[var(--border-hover)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/15 focus:border-[var(--accent)] cursor-pointer transition-all appearance-none"
            >
              <option value="All">All Source Languages</option>
              {languages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-[var(--text-muted)] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none transition-transform" />
          </div>
        </div>

        {/* 3. CATEGORY */}
        <div>
          <label 
            htmlFor="select-field"
            className="block text-[12px] font-medium uppercase tracking-wider text-[var(--text-secondary)] mb-1.5"
          >
            CATEGORY
          </label>
          <div className="relative">
            <select
              id="select-field"
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="w-full h-[40px] pl-3.5 pr-9 text-[13px] sm:text-[14px] bg-[var(--input-background)] border border-[var(--border)] hover:border-[var(--border-hover)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/15 focus:border-[var(--accent)] cursor-pointer transition-all appearance-none"
            >
              <option value="All">All Editorial Categories</option>
              {fields.map((fld) => (
                <option key={fld} value={fld}>
                  {fld}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-[var(--text-muted)] absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none transition-transform" />
          </div>
        </div>
      </div>
    </div>
  );
};
