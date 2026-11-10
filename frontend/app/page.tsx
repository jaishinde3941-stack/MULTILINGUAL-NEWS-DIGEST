"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { Header } from "@/components/Header";
import { HeroStats } from "@/components/HeroStats";
import { FilterBar } from "@/components/FilterBar";
import { ArticleCard } from "@/components/ArticleCard";
import { ArticleReaderModal } from "@/components/ArticleReaderModal";
import { AuthModal } from "@/components/AuthModal";
import { ProfileDrawer } from "@/components/ProfileDrawer";
import { 
  Article, FilterMetadata, AuthUser, BatchStatusResponse,
  fetchTrendingArticles, fetchFilteredArticles,
  fetchFilterMetadata, fetchCurrentUser, toggleBookmark, removeStoredToken,
  reprocessFailedArticles, rotateNewsBatch, fetchBatchStatus
} from "@/lib/api";
import { Flame, SlidersHorizontal, RefreshCw, AlertCircle } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"trending" | "explore">("trending");
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  const [batchStatus, setBatchStatus] = useState<BatchStatusResponse | null>(null);
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);
  const [isRotating, setIsRotating] = useState<boolean>(false);
  const [rotationMessage, setRotationMessage] = useState<string | null>(null);
  const [isTransitioningBatch, setIsTransitioningBatch] = useState<boolean>(false);

  // Theme Management (Light / Dark)
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    try {
      const current = (document.documentElement.getAttribute("data-theme") as "light" | "dark") ||
        (localStorage.getItem("akhbar_theme") as "light" | "dark") || "dark";
      setTheme(current);
    } catch {}
  }, []);

  const handleToggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next = prev === "dark" ? "light" : "dark";
      try {
        localStorage.setItem("akhbar_theme", next);
        document.documentElement.setAttribute("data-theme", next);
        if (next === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      } catch {}
      return next;
    });
  }, []);

  // User Auth & Modals
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [isProfileOpen, setIsProfileOpen] = useState<boolean>(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  // Filters State with guaranteed non-empty fallback metadata
  const [filterMetadata, setFilterMetadata] = useState<FilterMetadata>({
    regions: ["Gujarat", "India", "Kerala", "Maharashtra", "Tamil Nadu", "Telangana/Andhra Pradesh"],
    languages: ["Gujarati", "Hindi", "Malayalam", "Marathi", "Tamil", "Telugu"],
    fields: [
      "Agriculture & Rural",
      "Culture & Society",
      "Education & Jobs",
      "Entertainment & Cinema",
      "Finance & Economics",
      "Health & Wellness",
      "Politics",
      "States & Regional",
      "Technology & AI"
    ],
  });
  const [selectedRegion, setSelectedRegion] = useState<string>("All");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("All");
  const [selectedField, setSelectedField] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [debouncedSearch, setDebouncedSearch] = useState<string>("");

  // Refs for race-condition prevention and search focus
  const requestIdRef = useRef<number>(0);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const activeBatchIdRef = useRef<string | null>(activeBatchId);
  activeBatchIdRef.current = activeBatchId;
  const articlesLengthRef = useRef<number>(articles.length);
  articlesLengthRef.current = articles.length;

  // Debounce search query to avoid firing API requests on every single keystroke
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery.trim());
    }, 280);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const isFiltered =
    (selectedRegion !== "All") ||
    (selectedLanguage !== "All") ||
    (selectedField !== "All") ||
    debouncedSearch.length > 0;

  // Load User & Filter metadata on start
  useEffect(() => {
    let isMounted = true;
    const initData = async () => {
      try {
        const currentUser = await fetchCurrentUser();
        if (isMounted) setUser(currentUser);
      } catch (e) {
        console.error("Error loading user:", e);
      }

      try {
        const meta = await fetchFilterMetadata();
        if (isMounted && meta && meta.regions && meta.regions.length > 0) {
          setFilterMetadata(meta);
        }
      } catch (e) {
        console.error("Error loading filter metadata:", e);
      }
    };

    initData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch articles smoothly: only shows full skeletons on initial load (articles.length === 0)
  // When filtering or updating with articles already loaded, keeps current cards visible with a sleek top progress indicator
  const loadArticles = useCallback(async () => {
    const currentRequestId = ++requestIdRef.current;
    
    if (articlesLengthRef.current === 0) {
      setLoading(true);
    } else {
      setIsUpdating(true);
    }
    setError(null);

    try {
      const hasFilterActive =
        (selectedRegion && selectedRegion !== "All") ||
        (selectedLanguage && selectedLanguage !== "All") ||
        (selectedField && selectedField !== "All") ||
        debouncedSearch.length > 0;

      let items: Article[] = [];
      if (hasFilterActive || activeTab === "explore") {
        const data = await fetchFilteredArticles({
          region: selectedRegion,
          language: selectedLanguage,
          field: selectedField,
          search: debouncedSearch,
          limit: 50,
        });
        items = data.items;
      } else {
        const data = await fetchTrendingArticles(50);
        items = data.items;
      }

      // Discard stale out-of-order responses
      if (currentRequestId !== requestIdRef.current) return;

      if (items.length > 0) {
        setArticles(items);
        articlesLengthRef.current = items.length;
        if (items[0].batch_id) {
          setActiveBatchId(items[0].batch_id);
          activeBatchIdRef.current = items[0].batch_id;
        }
      } else if (hasFilterActive) {
        // Only set empty if user explicitly filtered and found no matches
        setArticles([]);
        articlesLengthRef.current = 0;
      }
      // If default feed returned empty (e.g. temporary DB lock/concurrency), retain existing articles!
    } catch (err: unknown) {
      if (currentRequestId === requestIdRef.current) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Failed to load articles");
        }
      }
    } finally {
      if (currentRequestId === requestIdRef.current) {
        setLoading(false);
        setIsUpdating(false);
      }
    }
  }, [activeTab, selectedRegion, selectedLanguage, selectedField, debouncedSearch]);

  const loadArticlesRef = useRef(loadArticles);
  loadArticlesRef.current = loadArticles;

  // Stable batch status refresher
  const refreshBatchStatus = useCallback(async () => {
    try {
      const status = await fetchBatchStatus();
      setBatchStatus(status);

      const currentBatchId = activeBatchIdRef.current;
      const currentCount = articlesLengthRef.current;

      // Auto-Sync:
      // 1. If active batch ID changed and we have a previous batch ID, reload new batch
      // 2. OR if articles are empty (currentCount === 0) and backend has active articles ready (status.active_count > 0)
      if (
        (status.active_batch_id && currentBatchId && status.active_batch_id !== currentBatchId) ||
        (currentCount === 0 && status.active_count > 0)
      ) {
        if (status.active_batch_id) {
          setActiveBatchId(status.active_batch_id);
          activeBatchIdRef.current = status.active_batch_id;
        }
        await loadArticlesRef.current();
      } else if (status.active_batch_id && !currentBatchId) {
        setActiveBatchId(status.active_batch_id);
        activeBatchIdRef.current = status.active_batch_id;
        if (currentCount === 0) {
          await loadArticlesRef.current();
        }
      }
    } catch {
      // Non-fatal background fetch
    }
  }, []);

  // Poll batch status: every 4s while refilling or initializing, every 15s when idle
  useEffect(() => {
    refreshBatchStatus();
    const isPreparing = batchStatus?.is_refilling || (batchStatus && batchStatus.active_count < 50);
    const intervalTime = isPreparing ? 4000 : 15000;
    const interval = setInterval(refreshBatchStatus, intervalTime);
    return () => clearInterval(interval);
  }, [refreshBatchStatus, batchStatus?.is_refilling, batchStatus?.active_count]);

  const handleRotateBatch = useCallback(async () => {
    if (isRotating) return;
    setIsRotating(true);
    setRotationMessage("Activating ready reserve batch (<100ms)...");
    try {
      const res = await rotateNewsBatch();
      const responseArticles = (res.articles && res.articles.length > 0)
        ? res.articles
        : (res.items && res.items.length > 0 ? res.items : []);

      if (res.status === "rotated" && responseArticles.length > 0) {
        // Immediate synchronous update to prevent race conditions with refreshBatchStatus
        const newBatchId = res.batch_id || res.active_batch_id || null;
        if (newBatchId) {
          setActiveBatchId(newBatchId);
          activeBatchIdRef.current = newBatchId;
        }
        setIsTransitioningBatch(true);
        setArticles(responseArticles);
        articlesLengthRef.current = responseArticles.length;
        setTimeout(() => {
          setIsTransitioningBatch(false);
        }, 120);

        const remaining = res.reserve_remaining ?? res.reserve_count ?? 0;
        setRotationMessage(`Rotated to 50 fresh articles! (Reserve refilling in background)`);
      } else if (res.status === "refill_in_progress") {
        if (responseArticles.length > 0) {
          setArticles((prev) => (prev.length === 0 ? responseArticles : prev));
          articlesLengthRef.current = responseArticles.length;
        }
        const ready = res.ready_count ?? res.reserve_count ?? 0;
        setRotationMessage(res.message || `Reserve batch refilling (${ready}/50 ready). Current active news retained.`);
      } else {
        if (responseArticles.length > 0) {
          setArticles((prev) => (prev.length === 0 ? responseArticles : prev));
          articlesLengthRef.current = responseArticles.length;
        }
        setRotationMessage(res.message || "Background prefetch actively gathering articles.");
      }
      await refreshBatchStatus();
      setTimeout(() => setRotationMessage(null), 4000);
    } catch (err: unknown) {
      console.error("Batch rotation failed:", err);
      const errMsg = err instanceof Error ? err.message : String(err);
      if (errMsg.toLowerCase().includes("refill") || errMsg.toLowerCase().includes("preparing")) {
        setRotationMessage("Reserve articles are currently being prepared in background. Retaining current articles.");
      } else {
        setRotationMessage("Unable to rotate batch immediately. Retaining current articles.");
      }
      setTimeout(() => setRotationMessage(null), 4000);
    } finally {
      setIsRotating(false);
    }
  }, [isRotating, refreshBatchStatus]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  const handleResetFilters = useCallback(() => {
    setSelectedRegion("All");
    setSelectedLanguage("All");
    setSelectedField("All");
    setSearchQuery("");
    setDebouncedSearch("");
  }, []);

  const handleTabChange = useCallback((tab: "trending" | "explore") => {
    setActiveTab(tab);
    if (tab === "trending") {
      handleResetFilters();
    }
  }, [handleResetFilters]);

  const handleToggleBookmark = useCallback(async (id: number) => {
    if (!user) {
      setIsAuthOpen(true);
      return;
    }
    try {
      const res = await toggleBookmark(id);
      setArticles((prev) =>
        prev.map((art) => (art.id === id ? { ...art, is_bookmarked: res.bookmarked } : art))
      );
    } catch (err) {
      console.error("Failed to toggle bookmark", err);
    }
  }, [user]);

  const handleLogout = useCallback(() => {
    removeStoredToken();
    setUser(null);
    setActiveTab("trending");
    handleResetFilters();
  }, [handleResetFilters]);

  // Stable card interaction callbacks for React.memo ArticleCard optimization
  const handleSelectArticle = useCallback((art: Article) => {
    setSelectedArticle(art);
  }, []);

  const handleCloseReader = useCallback(() => {
    setSelectedArticle(null);
  }, []);

  const handleArticleUpdated = useCallback((updated: Article) => {
    setSelectedArticle(updated);
    setArticles((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
  }, []);

  const handleFilterByRegion = useCallback((region: string) => {
    setSelectedRegion(region);
    setActiveTab("explore");
  }, []);

  const handleFilterByLanguage = useCallback((lang: string) => {
    setSelectedLanguage(lang);
    setActiveTab("explore");
  }, []);

  const handleFilterByField = useCallback((field: string) => {
    setSelectedField(field);
    setActiveTab("explore");
  }, []);

  const handleFilterByKeyword = useCallback((keyword: string) => {
    setSearchQuery(keyword);
    setDebouncedSearch(keyword);
    setActiveTab("explore");
  }, []);

  const handleFocusSearch = useCallback(() => {
    setActiveTab("explore");
    setTimeout(() => {
      searchInputRef.current?.focus();
    }, 50);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg)] text-[var(--text-primary)] transition-colors duration-200">
      {/* Sticky Compact Editorial Header with brand अख़बार वाले */}
      <Header
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenProfile={() => setIsProfileOpen(true)}
        onLogout={handleLogout}
        onRefreshFeeds={loadArticles}
        batchStatus={batchStatus}
        isRotating={isRotating}
        onRotateBatch={handleRotateBatch}
        rotationMessage={rotationMessage}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        onFocusSearch={handleFocusSearch}
      />

      {/* Sleek Non-Intrusive Progress Line right under sticky header - ZERO layout displacement */}
      <div 
        className={`fixed top-[68px] left-0 right-0 z-30 h-[2px] overflow-hidden pointer-events-none transition-opacity duration-300 ${
          isUpdating ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="h-full bg-[var(--accent)] w-1/3 animate-shimmer" />
      </div>

      <main className="flex-1 max-w-[1300px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Compact Editorial Heading replacing the old oversized Hero section */}
        <HeroStats
          articleCount={articles.length}
        />

        {/* Compact Editorial Filters Bar */}
        <FilterBar
          metadata={filterMetadata}
          selectedRegion={selectedRegion}
          setSelectedRegion={(reg) => {
            setSelectedRegion(reg);
            if (activeTab !== "explore" && reg !== "All") {
              setActiveTab("explore");
            }
          }}
          selectedLanguage={selectedLanguage}
          setSelectedLanguage={(lang) => {
            setSelectedLanguage(lang);
            if (activeTab !== "explore" && lang !== "All") {
              setActiveTab("explore");
            }
          }}
          selectedField={selectedField}
          setSelectedField={(field) => {
            setSelectedField(field);
            if (activeTab !== "explore" && field !== "All") {
              setActiveTab("explore");
            }
          }}
          searchQuery={searchQuery}
          setSearchQuery={(query) => {
            setSearchQuery(query);
            if (activeTab !== "explore" && query.trim()) {
              setActiveTab("explore");
            }
          }}
          onResetFilters={handleResetFilters}
          totalResults={articles.length}
          searchInputRef={searchInputRef}
        />

        {/* Section Heading & Reprocess Control */}
        <div className="flex items-center justify-between mb-6">
          <div>
            {isFiltered ? (
              <div>
                <h2 className="text-[20px] font-bold text-[var(--text-primary)] leading-tight mb-1">
                  Filtered Dispatches
                </h2>
                <p className="text-[13px] text-[var(--text-muted)]">
                  {[
                    selectedRegion !== "All" ? `Region: ${selectedRegion}` : null,
                    selectedLanguage !== "All" ? `Language: ${selectedLanguage}` : null,
                    selectedField !== "All" ? `Category: ${selectedField}` : null,
                    debouncedSearch ? `Search: "${debouncedSearch}"` : null,
                  ].filter(Boolean).join(" • ")}
                </p>
              </div>
            ) : activeTab === "trending" ? (
              <div>
                <h2 className="text-[20px] font-bold text-[var(--text-primary)] leading-tight mb-1">
                  Trending Stories
                </h2>
                <p className="text-[13px] text-[var(--text-muted)]">
                  The latest stories, thoughtfully summarized 😎.
                </p>
              </div>
            ) : (
              <div>
                <h2 className="text-[20px] font-bold text-[var(--text-primary)] leading-tight mb-1">
                  Explore Dispatches
                </h2>
                <p className="text-[13px] text-[var(--text-muted)]">
                  Filter by source languages, regions, and editorial beats.
                </p>
              </div>
            )}
          </div>

          {articles.some((a) => a.processing_status === "failed" || a.processing_status === "flagged") && (
            <button
              type="button"
              onClick={async () => {
                setIsIngesting(true);
                setIngestStatus("Reprocessing incomplete/flagged articles with Llama 3.2...");
                try {
                  await reprocessFailedArticles(25, "unprocessed");
                  setTimeout(async () => {
                    await loadArticles();
                    setIngestStatus("Reprocessing in progress...");
                    setTimeout(() => setIngestStatus(null), 3000);
                  }, 2000);
                } catch {
                  await loadArticles();
                } finally {
                  setIsIngesting(false);
                }
              }}
              disabled={isIngesting}
              className="px-2.5 py-1 rounded-md bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] text-[var(--text-primary)] font-medium text-xs flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50 shadow-xs"
            >
              <RefreshCw className={`w-3 h-3 text-[var(--accent)] ${isIngesting ? "animate-spin" : ""}`} />
              <span>Reprocess Incomplete</span>
            </button>
          )}
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-3.5 mb-5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-700 dark:text-rose-300 text-xs sm:text-sm flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-[var(--accent)] shrink-0" />
            <div className="flex-1">
              <span className="font-semibold">Unable to connect to backend:</span> {error}. Ensure FastAPI is running on port 8000.
            </div>
            <button
              type="button"
              onClick={loadArticles}
              className="px-2.5 py-1 bg-[var(--card)] border border-[var(--border)] rounded-md text-xs font-semibold text-[var(--text-primary)] transition-colors cursor-pointer"
            >
              Retry
            </button>
          </div>
        )}

        {/* Skeletons only on initial empty load */}
        {loading && articles.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="rounded-xl bg-[var(--surface)] border border-[var(--border)] p-4 space-y-3.5 animate-pulse h-80"
              >
                <div className="h-40 bg-[var(--surface-secondary)] rounded-lg" />
                <div className="h-3.5 bg-[var(--surface-secondary)] rounded w-1/4" />
                <div className="h-5 bg-[var(--surface-secondary)] rounded w-5/6" />
                <div className="h-12 bg-[var(--surface-secondary)] rounded" />
              </div>
            ))}
          </div>
        ) : articles.length > 0 ? (
          /* Articles Grid with smooth opacity transition without layout shifts */
          <div 
            className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 transition-opacity duration-250 ease-out ${
              isTransitioningBatch ? "opacity-40" : isUpdating ? "opacity-90" : "opacity-100"
            }`}
          >
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onSelect={handleSelectArticle}
                onToggleBookmark={handleToggleBookmark}
                isAuthenticated={!!user}
                onFilterByRegion={handleFilterByRegion}
                onFilterByLanguage={handleFilterByLanguage}
                onFilterByField={handleFilterByField}
                onFilterByKeyword={handleFilterByKeyword}
              />
            ))}
          </div>
        ) : (
          /* Empty State when no articles are present */
          <div className="text-center py-14 px-6 rounded-2xl bg-[var(--card)] border border-[var(--border)] max-w-lg mx-auto shadow-sm">
            {debouncedSearch || selectedRegion !== "All" || selectedLanguage !== "All" || selectedField !== "All" ? (
              <>
                <div className="w-12 h-12 rounded-xl bg-[var(--accent-subtle)] border border-[var(--accent-border)] text-[var(--accent)] flex items-center justify-center mx-auto mb-3.5">
                  <SlidersHorizontal className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-[var(--text-primary)] mb-1.5">No Matching Articles Found</h3>
                <p className="text-xs text-[var(--text-secondary)] mb-5 leading-relaxed">
                  No articles matched your active filters. Try clearing your filters or resetting the search query.
                </p>
                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="px-4 py-2 rounded-lg bg-[var(--bg)] hover:bg-[var(--bg-subtle)] text-[var(--text-primary)] text-xs font-semibold border border-[var(--border)] transition-all cursor-pointer"
                >
                  Reset Filters
                </button>
              </>
            ) : (
              <>
                <div className="w-12 h-12 rounded-xl bg-[var(--accent-subtle)] border border-[var(--accent-border)] text-[var(--accent)] flex items-center justify-center mx-auto mb-3.5">
                  <RefreshCw className={`w-5 h-5 ${batchStatus?.is_refilling || isRotating || isIngesting ? "animate-spin text-[var(--accent)]" : "text-[var(--accent)]"}`} />
                </div>
                <h3 className="text-base font-bold text-[var(--text-primary)] mb-1.5">
                  {batchStatus?.is_refilling
                    ? `Preparing Batch (${batchStatus.refill_progress?.ready ?? batchStatus.active_count ?? 0}/50 Articles Synthesized)`
                    : batchStatus && batchStatus.active_count >= 50
                    ? "50 Articles Ready for Display"
                    : "Initializing Global News Pipeline"}
                </h3>
                <p className="text-xs text-[var(--text-secondary)] mb-5 leading-relaxed">
                  {batchStatus?.refill_progress?.message || "Aggregating international RSS feeds and synthesizing executive English headlines and summaries with local Llama 3.2."}
                </p>

                <button
                  id="btn-main-ingest"
                  type="button"
                  onClick={async () => {
                    await handleRotateBatch();
                    await loadArticles();
                  }}
                  disabled={isRotating || isIngesting}
                  className="px-5 py-2.5 rounded-lg bg-[var(--accent)] hover:opacity-90 text-white text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 mx-auto shadow-sm"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRotating || isIngesting ? "animate-spin" : ""}`} />
                  <span>{isRotating ? "Rotating News..." : isIngesting ? "Aggregating Dispatches..." : "Load Active News"}</span>
                </button>

                {(rotationMessage || ingestStatus) && (
                  <p className="text-xs text-[var(--accent)] mt-3">{rotationMessage || ingestStatus}</p>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* Reader Modal with immediate unmounting on close */}
      <ArticleReaderModal
        article={selectedArticle}
        onClose={handleCloseReader}
        onArticleUpdated={handleArticleUpdated}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(newUser) => {
          setUser(newUser);
          loadArticles();
        }}
      />

      {/* Profile Drawer */}
      <ProfileDrawer
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        user={user}
        onLogout={handleLogout}
      />
    </div>
  );
}
