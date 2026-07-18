import { ApiError, USE_MOCK, delay, request, setAuthToken } from "./http";
import type { AuthProgress, AuthSession, AuthStage, GitHubProfile } from "./types";
import { mockProfile } from "./mock-data";

const SESSION_KEY = "atlas.session";

function readSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as AuthSession) : null;
  } catch {
    return null;
  }
}

function writeSession(session: AuthSession | null) {
  if (typeof window === "undefined") return;
  if (session) {
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    setAuthToken(session.token);
  } else {
    window.localStorage.removeItem(SESSION_KEY);
    setAuthToken(null);
  }
  window.dispatchEvent(new CustomEvent("atlas:auth-change"));
}

const STAGES: { stage: AuthStage; message: string; duration: number }[] = [
  { stage: "connecting", message: "Reaching GitHub", duration: 400 },
  { stage: "redirecting", message: "Redirecting to GitHub", duration: 500 },
  { stage: "authorizing", message: "Authorizing Atlas app", duration: 600 },
  { stage: "fetching_profile", message: "Fetching your profile", duration: 500 },
  { stage: "fetching_repositories", message: "Loading your repositories", duration: 600 },
  { stage: "completed", message: "Ready", duration: 200 },
];

export interface SignInOptions {
  signal?: AbortSignal;
  onProgress?: (progress: AuthProgress) => void;
  /** Force a specific error to test failure states. */
  simulate?: "network" | "unauthorized" | "expired";
}

export const AuthService = {
  getSession(): AuthSession | null {
    return readSession();
  },

  isAuthenticated(): boolean {
    const s = readSession();
    return !!s && s.expiresAt > Date.now();
  },

  async signInWithGitHub(opts: SignInOptions = {}): Promise<AuthSession> {
    const total = STAGES.reduce((n, s) => n + s.duration, 0);
    let elapsed = 0;
    for (const [i, s] of STAGES.entries()) {
      if (opts.signal?.aborted) throw new ApiError("Aborted", 0, "aborted");
      opts.onProgress?.({ stage: s.stage, message: s.message, progress: elapsed / total });
      await delay(s.duration, opts.signal);
      elapsed += s.duration;
      // Fail at the "authorizing" stage when simulating.
      if (opts.simulate && i === 2) {
        const codeByKind = {
          network: { status: 0, code: "network_error", msg: "We couldn't reach GitHub. Check your connection and retry." },
          unauthorized: { status: 401, code: "unauthorized", msg: "Atlas isn't authorized on your account. Approve the app and retry." },
          expired: { status: 419, code: "session_expired", msg: "Your session expired mid-flow. Please sign in again." },
        }[opts.simulate];
        throw new ApiError(codeByKind.msg, codeByKind.status, codeByKind.code);
      }
    }
    opts.onProgress?.({ stage: "completed", message: "Ready", progress: 1 });

    if (USE_MOCK) {
      const session: AuthSession = {
        token: `mock.${Math.random().toString(36).slice(2)}.${Date.now()}`,
        expiresAt: Date.now() + 30 * 86_400_000,
        profile: mockProfile,
      };
      writeSession(session);
      return session;
    }

    const session = await request<AuthSession>("/auth/github", { method: "POST", auth: false, signal: opts.signal });
    writeSession(session);
    return session;
  },

  async refreshProfile(signal?: AbortSignal): Promise<GitHubProfile> {
    if (USE_MOCK) {
      await delay(300, signal);
      const session = readSession();
      if (!session) throw new ApiError("Not signed in", 401, "unauthorized");
      const refreshed: GitHubProfile = { ...session.profile, followers: session.profile.followers + Math.floor(Math.random() * 3) };
      writeSession({ ...session, profile: refreshed });
      return refreshed;
    }
    const profile = await request<GitHubProfile>("/auth/profile", { signal });
    const session = readSession();
    if (session) writeSession({ ...session, profile });
    return profile;
  },

  signOut() {
    writeSession(null);
  },

  async switchAccount(opts: SignInOptions = {}): Promise<AuthSession> {
    this.signOut();
    return this.signInWithGitHub(opts);
  },
};

export const AUTH_EVENT = "atlas:auth-change";
