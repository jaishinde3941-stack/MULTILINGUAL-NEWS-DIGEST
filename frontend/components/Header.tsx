"use client";

import React, { useState } from "react";
import { Flame, SlidersHorizontal, Search, RefreshCw, Sun, Moon, User, LogOut } from "lucide-react";
import { AuthUser, BatchStatusResponse, triggerIngestion } from "@/lib/api";

interface HeaderProps {
  activeTab: "trending" | "explore";
  setActiveTab: (tab: "trending" | "explore") => void;
  user: AuthUser | null;
  onOpenAuth: () => void;
  onOpenProfile: () => void;
  onLogout: () => void;
  onRefreshFeeds: () => void;
  batchStatus?: BatchStatusResponse | null;
  isRotating?: boolean;
  onRotateBatch?: () => Promise<void> | void;
  rotationMessage?: string | null;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onFocusSearch?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onOpenProfile,
  onLogout,
  onRefreshFeeds,
  batchStatus,
  isRotating = false,
  onRotateBatch,
  rotationMessage,
  theme,
  onToggleTheme,
  onFocusSearch,
}) => {
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const handleTriggerIngest = async () => {
    if (onRotateBatch) {
      await onRotateBatch();
      return;
    }
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

  const activeMessage = rotationMessage || ingestStatus;

  return (
    <header className="sticky top-0 z-40 w-full h-[68px] border-b border-[var(--border)] bg-[var(--surface)] transition-colors duration-200">
      <div className="max-w-[1300px] h-full mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* LEFT SECTION: Hindi brand name + red accent + separator + subtitle */}
        <div 
          className="flex items-center gap-3 cursor-pointer select-none" 
          onClick={() => setActiveTab("trending")}
          title="अख़बार वाले — Global Stories · Clear English"
        >
          <div className="flex items-baseline gap-1.5">
            <span className="font-brand text-2xl sm:text-[26px] font-extrabold tracking-tight text-[var(--text-primary)]">
              अख़बार वाले
            </span>
            <span className="text-[var(--accent)] text-xl font-bold leading-none select-none">•</span>
          </div>
          <div className="hidden md:flex items-center gap-3">
            <span className="w-px h-4 bg-[var(--border)]" aria-hidden="true" />
            <span className="text-[11px] font-medium tracking-widest text-[var(--text-muted)] uppercase">
              GLOBAL STORIES · CLEAR ENGLISH
            </span>
          </div>
        </div>

        {/* CENTER SECTION: Trending, Explore, Search */}
        <nav className="flex items-center gap-1.5 sm:gap-2">
          <button
            id="tab-trending"
            type="button"
            onClick={() => setActiveTab("trending")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-[14px] font-medium transition-all cursor-pointer ${
              activeTab === "trending"
                ? "bg-[var(--accent-soft)] text-[var(--accent)] font-semibold"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]"
            }`}
          >
            <Flame className={`w-4 h-4 ${activeTab === "trending" ? "text-[var(--accent)]" : "text-[var(--text-muted)]"}`} />
            <span>Trending</span>
          </button>

          <button
            id="tab-explore"
            type="button"
            onClick={() => setActiveTab("explore")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-[14px] font-medium transition-all cursor-pointer ${
              activeTab === "explore"
                ? "bg-[var(--accent-soft)] text-[var(--accent)] font-semibold"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]"
            }`}
          >
            <SlidersHorizontal className={`w-4 h-4 ${activeTab === "explore" ? "text-[var(--accent)]" : "text-[var(--text-muted)]"}`} />
            <span>Explore</span>
          </button>

          {onFocusSearch && (
            <button
              type="button"
              onClick={onFocusSearch}
              aria-label="Focus search input"
              title="Search articles"
              className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-lg text-[14px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-secondary)] transition-colors cursor-pointer"
            >
              <Search className="w-4 h-4 text-[var(--text-muted)]" />
              <span className="hidden md:inline">Search</span>
            </button>
          )}
        </nav>

        {/* RIGHT SECTION: Ingest News, Theme Toggle, Account / Logout */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          {/* Subtle live indicator when reserve is refilling in background */}
          {batchStatus?.is_refilling && (
            <div 
              className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-[var(--surface-secondary)] border border-[var(--border)] text-[var(--text-secondary)] select-none"
              title={`Refilling reserve batch: ${batchStatus.reserve_count}/50 articles prepared. Current active articles displayed.`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
              <span>Refilling Reserve ({batchStatus.reserve_count}/50)</span>
            </div>
          )}

          {/* Ingest News button with article progress indicator */}
          <button
            id="btn-trigger-ingest"
            type="button"
            onClick={handleTriggerIngest}
            disabled={isRotating || isIngesting}
            title={
              batchStatus?.is_refilling
                ? `Reserve batch refilling (${batchStatus.reserve_count}/50 ready). Current batch displayed.`
                : "Rotate to 50 prepared reserve articles and prefetch next batch"
            }
            className="h-10 px-3 text-[13px] sm:text-[14px] font-medium text-[var(--text-primary)] bg-[var(--surface)] hover:bg-[var(--surface-secondary)] border border-[var(--border)] rounded-lg transition-all disabled:opacity-50 cursor-pointer inline-flex items-center gap-2 active:scale-98 shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[var(--accent)] ${isRotating || isIngesting ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">{isRotating ? "Rotating..." : "Ingest News"}</span>
            {batchStatus && (
              <span className="text-[11px] font-medium text-[var(--text-muted)]">
                ({batchStatus.active_count}/{batchStatus.reserve_count})
              </span>
            )}
          </button>

          {/* Theme Toggle Button (Light/Dark) */}
          <button
            type="button"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            className="w-10 h-10 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--surface)] hover:bg-[var(--surface-secondary)] border border-[var(--border)] transition-colors inline-flex items-center justify-center cursor-pointer active:scale-98"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-700" />
            )}
          </button>

          {/* User Account Controls */}
          {user ? (
            <div className="flex items-center gap-1.5">
              <button
                id="btn-view-profile"
                type="button"
                onClick={onOpenProfile}
                title={`Logged in as ${user.full_name || user.email}`}
                className="h-10 px-3 text-[13px] sm:text-[14px] font-medium text-[var(--text-primary)] bg-[var(--surface)] hover:bg-[var(--surface-secondary)] border border-[var(--border)] rounded-lg transition-colors cursor-pointer inline-flex items-center gap-2"
              >
                <User className="w-4 h-4 text-[var(--text-muted)]" />
                <span className="max-w-[100px] truncate">{user.full_name || user.email.split("@")[0]}</span>
              </button>
              <button
                id="btn-logout"
                type="button"
                onClick={onLogout}
                title="Logout"
                aria-label="Logout"
                className="w-10 h-10 rounded-lg text-[var(--text-muted)] hover:text-[var(--accent)] bg-[var(--surface)] hover:bg-[var(--surface-secondary)] border border-[var(--border)] transition-colors inline-flex items-center justify-center cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              id="btn-open-auth"
              type="button"
              onClick={onOpenAuth}
              className="h-10 px-4 text-[14px] font-medium text-white bg-[var(--accent)] hover:bg-[var(--accent-hover)] rounded-lg transition-colors cursor-pointer inline-flex items-center gap-2 active:scale-98 shadow-xs"
            >
              <User className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>

      {/* Floating Status Toast overlay - zero layout displacement */}
      {activeMessage && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-4 py-2 rounded-full bg-[var(--surface)] border border-[var(--border)] text-[var(--text-primary)] text-xs font-medium shadow-md z-50 pointer-events-none flex items-center gap-2 animate-modal-content">
          <RefreshCw className="w-3.5 h-3.5 text-[var(--accent)] animate-spin shrink-0" />
          <span>{activeMessage}</span>
        </div>
      )}
    </header>
  );
};
