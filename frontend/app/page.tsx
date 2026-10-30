"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "@/components/Header";
import { HeroStats } from "@/components/HeroStats";
import { FilterBar } from "@/components/FilterBar";
import { ArticleCard } from "@/components/ArticleCard";
import { ArticleReaderModal } from "@/components/ArticleReaderModal";
import { OnboardingModal } from "@/components/OnboardingModal";
import { AuthModal } from "@/components/AuthModal";
import { ProfileDrawer } from "@/components/ProfileDrawer";
import { 
  Article, FilterMetadata, AuthUser,
  fetchTrendingArticles, fetchForYouArticles, fetchFilteredArticles,
  fetchFilterMetadata, fetchCurrentUser, toggleBookmark, removeStoredToken, triggerIngestion,
  reprocessFailedArticles
} from "@/lib/api";
import { Sparkles, Flame, SlidersHorizontal, RefreshCw, AlertCircle, BookOpen } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"foryou" | "trending" | "explore">("trending");
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  // User Auth & Modals
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [isQuizOpen, setIsQuizOpen] = useState<boolean>(false);
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

  // Load User & Filter metadata on start
  useEffect(() => {
    const initData = async () => {
      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
        if (currentUser) {
          setActiveTab("foryou");
        } else {
          setActiveTab("trending");
        }
      } catch (e) {
        console.error("Error loading user:", e);
        setActiveTab("trending");
      }

      try {
        const meta = await fetchFilterMetadata();
        if (meta && meta.regions && meta.regions.length > 0) {
          setFilterMetadata(meta);
        }
      } catch (e) {
        console.error("Error loading filter metadata:", e);
      }
    };

    initData();
  }, []);

  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    setIngestStatus("Aggregating international RSS & translating dispatches...");
    try {
      await triggerIngestion(2);
      setIngestStatus("Ingestion complete!");
      await loadArticles();
      setTimeout(() => setIngestStatus(null), 3000);
    } catch {
      await loadArticles();
      setIngestStatus("Ingestion process completed.");
      setTimeout(() => setIngestStatus(null), 3000);
    } finally {
      setIsIngesting(false);
    }
  };

  const isFiltered =
    (selectedRegion && selectedRegion !== "All") ||
    (selectedLanguage && selectedLanguage !== "All") ||
    (selectedField && selectedField !== "All") ||
    searchQuery.trim().length > 0;

  // Fetch articles based on active filters or active tab
  const loadArticles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const hasFilterActive =
        (selectedRegion && selectedRegion !== "All") ||
        (selectedLanguage && selectedLanguage !== "All") ||
        (selectedField && selectedField !== "All") ||
        searchQuery.trim().length > 0;

      if (hasFilterActive || activeTab === "explore") {
        const data = await fetchFilteredArticles({
          region: selectedRegion,
          language: selectedLanguage,
          field: selectedField,
          search: searchQuery,
          limit: 50,
        });
        setArticles(data.items);
      } else if (activeTab === "foryou") {
        const data = await fetchForYouArticles(25);
        setArticles(data.items);
      } else {
        const data = await fetchTrendingArticles(25);
        setArticles(data.items);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load articles");
      }
    } finally {
      setLoading(false);
    }
  }, [activeTab, selectedRegion, selectedLanguage, selectedField, searchQuery]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  const handleResetFilters = () => {
    setSelectedRegion("All");
    setSelectedLanguage("All");
    setSelectedField("All");
    setSearchQuery("");
  };

  const handleTabChange = (tab: "foryou" | "trending" | "explore") => {
    setActiveTab(tab);
    if (tab === "trending" || tab === "foryou") {
      handleResetFilters();
    }
  };

  const handleToggleBookmark = async (id: number) => {
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
  };

  const handleLogout = () => {
    removeStoredToken();
    setUser(null);
    setActiveTab("trending");
    handleResetFilters();
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-slate-100">
      {/* Sticky Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={handleTabChange}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenQuiz={() => {
          if (!user) {
            setIsAuthOpen(true);
          } else {
            setIsQuizOpen(true);
          }
        }}
        onOpenProfile={() => setIsProfileOpen(true)}
        onLogout={handleLogout}
        onRefreshFeeds={loadArticles}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Banner with live stats */}
        <HeroStats
          user={user}
          onOpenQuiz={() => {
            if (!user) {
              setIsAuthOpen(true);
            } else {
              setIsQuizOpen(true);
            }
          }}
          articleCount={articles.length}
        />

        {/* Dynamic Filters Bar */}
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
        />

        {/* Prompt banner for logged-in user who hasn't completed quiz */}
        {user && !user.completed_onboarding && activeTab === "foryou" && (
          <div className="mb-6 p-4 rounded-2xl bg-gradient-to-r from-indigo-950/80 via-blue-950/70 to-purple-950/80 border border-indigo-500/40 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shrink-0">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Unlock Your Personalized Match Percentages</h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Complete the quick 15-question strategic questionnaire to activate interest-weighted ranking and see exact % Match affinity on your dispatches.
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsQuizOpen(true)}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition-all shrink-0 cursor-pointer"
            >
              Start 15-Question Quiz
            </button>
          </div>
        )}

        {/* Feed Section Title */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            {isFiltered ? (
              <>
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <SlidersHorizontal className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Filtered Intelligence Feed</h2>
                  <p className="text-xs text-slate-400">
                    Active Filters: {[
                      selectedRegion !== "All" ? `Region: ${selectedRegion}` : null,
                      selectedLanguage !== "All" ? `Language: ${selectedLanguage}` : null,
                      selectedField !== "All" ? `Field: ${selectedField}` : null,
                      searchQuery.trim() ? `Search: "${searchQuery.trim()}"` : null,
                    ].filter(Boolean).join(" • ")}
                  </p>
                </div>
              </>
            ) : activeTab === "foryou" ? (
              <>
                <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Your Personalized Digest</h2>
                  <p className="text-xs text-slate-400">
                    {user?.completed_onboarding 
                      ? "Weighted by your 15-question interest graph with live % Match affinity scores" 
                      : "Curated multilingual dispatches translated in real time"}
                  </p>
                </div>
              </>
            ) : activeTab === "trending" ? (
              <>
                <div className="w-8 h-8 rounded-lg bg-orange-500/10 border border-orange-500/30 flex items-center justify-center text-orange-400">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Global Trending Headlines</h2>
                  <p className="text-xs text-slate-400">
                    Top breaking developments across regional and national world press
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <SlidersHorizontal className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Custom Cross-Section</h2>
                  <p className="text-xs text-slate-400">Filter articles across regions, source languages, and editorial fields</p>
                </div>
              </>
            )}
          </div>

          {articles.some((a) => a.processing_status === "failed" || a.processing_status === "flagged") && (
            <button
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
              className="px-3 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 font-semibold text-xs flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? "animate-spin" : ""}`} />
              <span>Reprocess Incomplete</span>
            </button>
          )}
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 mb-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <div className="flex-1">
              <span className="font-semibold">Unable to connect to backend:</span> {error}. Make sure the FastAPI server is running on port 8000.
            </div>
            <button
              onClick={loadArticles}
              className="px-3 py-1 bg-rose-600/30 hover:bg-rose-600 rounded-lg text-xs font-bold text-white transition-colors cursor-pointer"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading Skeletons */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="rounded-2xl bg-slate-900/50 border border-slate-800/80 p-5 space-y-4 animate-pulse h-96"
              >
                <div className="h-44 bg-slate-800/60 rounded-xl" />
                <div className="h-4 bg-slate-800 rounded w-1/3" />
                <div className="h-6 bg-slate-800 rounded w-5/6" />
                <div className="h-16 bg-slate-800/40 rounded-xl" />
              </div>
            ))}
          </div>
        ) : activeTab === "foryou" && !user ? (
          /* Guest Mode prompt for "For You" feed */
          <div className="text-center py-16 px-6 rounded-3xl bg-slate-900/40 border border-slate-800/80 max-w-xl mx-auto shadow-2xl">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-7 h-7" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Personalized Intelligence Feed</h3>
            <p className="text-sm text-slate-300 mb-6 leading-relaxed">
              The &quot;For You&quot; feed calibrates a 15-question strategic interest questionnaire to dynamically rank reporting and display exact <strong className="text-indigo-300">% Match</strong> percentages. 
              All other features—including Global Trending, Explore & Filter, Bilingual Reading, and Audio Playback—remain fully accessible in Guest Mode.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                onClick={() => setIsAuthOpen(true)}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
              >
                Sign In or Create Account
              </button>
              <button
                onClick={() => setActiveTab("trending")}
                className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
              >
                Browse Trending News
              </button>
            </div>
          </div>
        ) : articles.length > 0 ? (
          /* Articles Grid with interactive filter callbacks */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onSelect={(art) => setSelectedArticle(art)}
                onToggleBookmark={handleToggleBookmark}
                isAuthenticated={!!user}
                hasCompletedQuiz={!!user?.completed_onboarding}
                onFilterByRegion={(region) => {
                  setSelectedRegion(region);
                  setActiveTab("explore");
                }}
                onFilterByLanguage={(lang) => {
                  setSelectedLanguage(lang);
                  setActiveTab("explore");
                }}
                onFilterByField={(field) => {
                  setSelectedField(field);
                  setActiveTab("explore");
                }}
                onFilterByKeyword={(keyword) => {
                  setSearchQuery(keyword);
                  setActiveTab("explore");
                }}
              />
            ))}
          </div>
        ) : (
          /* Empty State when no articles are present */
          <div className="text-center py-16 px-6 rounded-3xl bg-slate-900/40 border border-slate-800/80 max-w-xl mx-auto shadow-2xl">
            {searchQuery || selectedRegion !== "All" || selectedLanguage !== "All" || selectedField !== "All" ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto mb-4">
                  <SlidersHorizontal className="w-7 h-7" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">No Matching Articles Found</h3>
                <p className="text-sm text-slate-300 mb-6 leading-relaxed">
                  No articles matched your active filter selections. Try clearing your filters or resetting the search query.
                </p>
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={handleResetFilters}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
                  >
                    Reset Filters
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto mb-5 shadow-lg shadow-blue-500/10">
                  <RefreshCw className={`w-8 h-8 ${isIngesting ? "animate-spin text-blue-400" : "text-blue-400"}`} />
                </div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-3">
                  <span>Live Aggregation Pipeline</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">No Articles Ingested Yet</h3>
                <p className="text-sm text-slate-300 mb-6 leading-relaxed">
                  The intelligence repository is waiting for initial ingestion. Click below to query active international feeds, perform real-time translations, and compile executive briefings.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                  <button
                    id="btn-main-ingest"
                    onClick={handleTriggerIngest}
                    disabled={isIngesting}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-bold shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${isIngesting ? "animate-spin" : ""}`} />
                    <span>{isIngesting ? "Aggregating & Translating Dispatches..." : "Ingest Global News Now"}</span>
                  </button>
                </div>
                {ingestStatus && (
                  <p className="text-xs text-blue-400 mt-4 animate-pulse">{ingestStatus}</p>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* Reader Modal */}
      <ArticleReaderModal
        article={selectedArticle}
        onClose={() => setSelectedArticle(null)}
        onArticleUpdated={(updated) => {
          setSelectedArticle(updated);
          setArticles((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
        }}
      />

      {/* 15-Question Onboarding Modal */}
      <OnboardingModal
        isOpen={isQuizOpen}
        onClose={() => {
          setIsQuizOpen(false);
          loadArticles();
        }}
        isAuthenticated={!!user}
        onRequireAuth={() => setIsAuthOpen(true)}
        onComplete={(profile) => {
          if (user) {
            setUser({ ...user, completed_onboarding: profile.completed_onboarding });
          }
          loadArticles();
        }}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(newUser) => {
          setUser(newUser);
          if (!newUser.completed_onboarding) {
            setIsQuizOpen(true);
          }
          loadArticles();
        }}
      />

      {/* Profile Drawer */}
      <ProfileDrawer
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        user={user}
        onRetakeQuiz={() => setIsQuizOpen(true)}
        onLogout={handleLogout}
      />
    </div>
  );
}
