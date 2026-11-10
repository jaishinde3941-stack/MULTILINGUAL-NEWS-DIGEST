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
  canonical_url?: string;
  batch_id?: string;
  batch_state?: "active" | "reserve" | "consumed";
}

export interface BatchStatusResponse {
  active_count: number;
  reserve_count: number;
  consumed_count: number;
  history_count: number;
  target_batch_size?: number;
  active_batch_id?: string;
  is_refilling: boolean;
  can_rotate?: boolean;
  refill_progress: {
    target: number;
    ready?: number;
    current?: number;
    status: string;
    message?: string;
  };
  message?: string;
}

export interface BatchRotateResponse {
  status: "rotated" | "refill_in_progress" | "empty" | "success";
  message: string;
  batch_id?: string;
  active_batch_id?: string;
  count: number;
  rotated_count?: number;
  items?: Article[];
  articles: Article[];
  reserve_remaining: number;
  active_count?: number;
  reserve_count?: number;
  ready_count?: number;
  is_refilling: boolean;
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

export interface UserProfile {
  id: number;
  user_id: number;
  email?: string;
  full_name?: string;
  preferred_languages?: string[];
  preferred_regions?: string[];
  preferred_fields?: string[];
  updated_at?: string;
}

export interface AuthUser {
  id: number;
  email: string;
  full_name?: string;
  completed_onboarding?: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name?: string;
  completed_onboarding?: boolean;
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
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
  };
  const token = getStoredToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

// API Functions
export async function fetchTrendingArticles(limit: number = 50): Promise<ArticleListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/articles/trending?limit=${limit}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch trending articles");
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

export async function rotateNewsBatch(): Promise<BatchRotateResponse> {
  const targetUrl = `${API_BASE_URL}/api/ingest/rotate`;
  try {
    const res = await fetch(targetUrl, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      const detail = errBody?.detail || errBody?.message || `HTTP ${res.status}`;
      throw new Error(`Batch rotation failed: ${detail}`);
    }
    return res.json();
  } catch (err: unknown) {
    // If direct cross-origin request hit a network or CORS drop, fallback to same-origin Next.js proxy
    if (typeof window !== "undefined" && API_BASE_URL && API_BASE_URL.startsWith("http")) {
      try {
        const proxyRes = await fetch("/api/ingest/rotate", {
          method: "POST",
          headers: getAuthHeaders(),
        });
        if (proxyRes.ok) {
          return proxyRes.json();
        }
      } catch {
        // Fallback also failed, bubble up original error
      }
    }
    throw err;
  }
}

export async function fetchBatchStatus(): Promise<BatchStatusResponse> {
  const targetUrl = `${API_BASE_URL}/api/ingest/batch-status`;
  try {
    const res = await fetch(targetUrl, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch batch status");
    return res.json();
  } catch (err: unknown) {
    if (typeof window !== "undefined" && API_BASE_URL && API_BASE_URL.startsWith("http")) {
      try {
        const proxyRes = await fetch("/api/ingest/batch-status", {
          headers: getAuthHeaders(),
          cache: "no-store",
        });
        if (proxyRes.ok) return proxyRes.json();
      } catch {}
    }
    throw err;
  }
}

export async function triggerBatchRefill(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/ingest/refill`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to trigger batch refill");
  return res.json();
}
