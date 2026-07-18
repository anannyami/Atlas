// Typed HTTP client for the Atlas API.
// Backed by fetch. AbortController-aware. Retry/backoff. Normalized errors.

const BASE_URL = (import.meta.env.VITE_ATLAS_API_URL as string | undefined) ?? "";
const AUTH_HEADER = "Authorization";
const TOKEN_STORAGE_KEY = "atlas.api.token";

export class ApiError extends Error {
  status: number;
  code: string;
  details?: unknown;

  constructor(message: string, status: number, code: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null | Array<string | number>>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  retries?: number;
  timeoutMs?: number;
  auth?: boolean;
}

let inMemoryToken: string | null = null;

export function setAuthToken(token: string | null) {
  inMemoryToken = token;
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  else window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function readAuthToken(): string | null {
  if (inMemoryToken) return inMemoryToken;
  if (typeof window === "undefined") return null;
  inMemoryToken = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  return inMemoryToken;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const base = BASE_URL || "";
  const full = path.startsWith("http") ? path : `${base}${path.startsWith("/") ? path : `/${path}`}`;
  if (!query) return full;
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined || v === null) continue;
    if (Array.isArray(v)) v.forEach((it) => qs.append(k, String(it)));
    else qs.set(k, String(v));
  }
  const s = qs.toString();
  return s ? `${full}${full.includes("?") ? "&" : "?"}${s}` : full;
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => {
      clearTimeout(t);
      reject(new ApiError("Aborted", 0, "aborted"));
    });
  });
}

export async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const {
    method = "GET",
    body,
    query,
    headers = {},
    signal,
    retries = 2,
    timeoutMs = 20_000,
    auth = true,
  } = opts;

  const url = buildUrl(path, query);
  const finalHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };
  if (body !== undefined && !(body instanceof FormData)) {
    finalHeaders["Content-Type"] = finalHeaders["Content-Type"] ?? "application/json";
  }
  if (auth) {
    const token = readAuthToken();
    if (token) finalHeaders[AUTH_HEADER] = `Bearer ${token}`;
  }

  let attempt = 0;
  let lastError: unknown;
  while (attempt <= retries) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    const onAbort = () => controller.abort();
    signal?.addEventListener("abort", onAbort);

    try {
      const res = await fetch(url, {
        method,
        headers: finalHeaders,
        body: body === undefined ? undefined : body instanceof FormData ? body : JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeout);
      signal?.removeEventListener("abort", onAbort);

      if (!res.ok) {
        let payload: unknown = null;
        try {
          payload = await res.json();
        } catch {
          /* ignore */
        }
        const code =
          (payload as { code?: string })?.code ??
          (res.status === 401 ? "unauthorized" : res.status === 404 ? "not_found" : "http_error");
        const message =
          (payload as { message?: string })?.message ?? `Request failed with ${res.status}`;
        throw new ApiError(message, res.status, code, payload);
      }

      if (res.status === 204) return undefined as T;
      const ct = res.headers.get("content-type") ?? "";
      if (ct.includes("application/json")) return (await res.json()) as T;
      return (await res.text()) as unknown as T;
    } catch (err) {
      clearTimeout(timeout);
      signal?.removeEventListener("abort", onAbort);
      lastError = err;
      if (err instanceof ApiError && err.code === "aborted") throw err;
      if (signal?.aborted) throw new ApiError("Aborted", 0, "aborted");
      // Retry only network errors or 5xx
      const isRetryable =
        !(err instanceof ApiError) || (err.status >= 500 && err.status < 600);
      if (attempt === retries || !isRetryable) throw err;
      const backoff = 250 * Math.pow(2, attempt);
      await sleep(backoff, signal);
      attempt++;
    }
  }
  throw lastError instanceof Error ? lastError : new ApiError("Unknown error", 0, "unknown");
}

// Convenience — used by mock adapters to simulate latency + abort.
export function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return sleep(ms, signal);
}

export const USE_MOCK = !BASE_URL;
