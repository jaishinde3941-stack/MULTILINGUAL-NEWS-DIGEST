const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface Article {
  id: number;
  source_url: string;
  source_name: string;
  original_language: string;
  original_title: string;
  original_content: string;
  original_summary?: string;
  english_title: string;
  english_summary: string;
  english_content: string;
  region: string;
  subregion?: string;
  field: string;
  keywords: string[];
  trending: boolean;
  trending_score: number;
  processing_status?: "completed" | "pending" | "failed" | "flagged";
  processing_error?: string;
  summary_word_count?: number;
  image_url?: string;
  published_at: string;
  created_at: string;
  match_score?: number;
  is_bookmarked?: boolean;
}

export interface ArticleListResponse {
  total: number;
  items: Article[];
}

export interface FilterMetadata {
  regions: string[];
  languages: string[];
  fields: string[];
}

export interface QuizOption {
  id: string;
  label: string;
  description?: string;
  icon?: string;
  weight_map: Record<string, number>;
}

export interface QuizQuestion {
  id: number;
  dimension: "region" | "field" | "language";
  title: string;
  subtitle: string;
  is_multi_select: boolean;
  options: QuizOption[];
}

export interface QuizListResponse {
  total_questions: number;
  questions: QuizQuestion[];
}

export interface UserProfile {
  id: number;
  user_id: number;
  completed_onboarding: boolean;
  interest_weights: Record<string, number>;
  preferred_languages: string[];
  preferred_regions: string[];
  preferred_fields: string[];
  quiz_answers: Record<string, string[]>;
  updated_at?: string;
}

export interface AuthUser {
  id: number;
  email: string;
  full_name?: string;
  completed_onboarding: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name?: string;
  completed_onboarding: boolean;
}

// Token management in localStorage
export const getStoredToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("news_digest_token");
};

export const setStoredToken = (token: string): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem("news_digest_token", token);
  }
};

export const removeStoredToken = (): void => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("news_digest_token");
  }
};

const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getStoredToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

// API Functions
export async function fetchTrendingArticles(limit: number = 20): Promise<ArticleListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/articles/trending?limit=${limit}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch trending articles");
  return res.json();
}

export async function fetchForYouArticles(limit: number = 20): Promise<ArticleListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/articles/foryou?limit=${limit}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch For You articles");
  return res.json();
}

export async function fetchFilteredArticles(params: {
  region?: string;
  language?: string;
  field?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<ArticleListResponse> {
  const query = new URLSearchParams();
  if (params.region && params.region !== "All") query.append("region", params.region);
  if (params.language && params.language !== "All") query.append("language", params.language);
  if (params.field && params.field !== "All") query.append("field", params.field);
  if (params.search) query.append("search", params.search);
  if (params.limit) query.append("limit", params.limit.toString());
  if (params.offset) query.append("offset", params.offset.toString());

  const res = await fetch(`${API_BASE_URL}/api/articles?${query.toString()}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to filter articles");
  return res.json();
}

export async function fetchFilterMetadata(): Promise<FilterMetadata> {
  const res = await fetch(`${API_BASE_URL}/api/articles/meta/filters`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch filter metadata");
  return res.json();
}

export async function fetchArticleById(id: number): Promise<Article> {
  const res = await fetch(`${API_BASE_URL}/api/articles/${id}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch article");
  return res.json();
}

export async function reprocessArticle(articleId: number): Promise<Article> {
  const res = await fetch(`${API_BASE_URL}/api/articles/${articleId}/reprocess`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to reprocess article");
  return res.json();
}

export async function reprocessFailedArticles(limit: number = 25, mode: string = "unprocessed"): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/ingest/reprocess?limit=${limit}&mode=${mode}&run_async=true`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to trigger background reprocessing");
  return res.json();
}

export async function toggleBookmark(id: number): Promise<{ bookmarked: boolean; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/articles/${id}/bookmark`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to toggle bookmark");
  return res.json();
}

export async function fetchOnboardingQuestions(): Promise<QuizListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/onboarding/questions`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch onboarding questions");
  return res.json();
}

export async function submitOnboarding(answers: { question_id: number; selected_option_ids: string[] }[]): Promise<UserProfile> {
  const res = await fetch(`${API_BASE_URL}/api/onboarding/submit`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ answers }),
  });
  if (!res.ok) throw new Error("Failed to submit onboarding answers");
  return res.json();
}

export async function fetchUserProfile(): Promise<UserProfile> {
  const res = await fetch(`${API_BASE_URL}/api/users/profile`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export async function registerUser(email: string, password: string, fullName?: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Registration failed" }));
    throw new Error(errorData.detail || "Registration failed");
  }
  return res.json();
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(errorData.detail || "Invalid email or password");
  }
  return res.json();
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const token = getStoredToken();
  if (!token) return null;
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) {
      removeStoredToken();
      return null;
    }
    return res.json();
  } catch {
    return null;
  }
}

export async function triggerIngestion(maxPerFeed: number = 2): Promise<{ message: string; count: number }> {
  const res = await fetch(`${API_BASE_URL}/api/ingest/trigger?max_per_feed=${maxPerFeed}&run_async=false`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to trigger ingestion");
  return res.json();
}
