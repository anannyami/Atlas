import { USE_MOCK, delay, request } from "./http";
import { enrichedRepositories, mockProfile } from "./mock-data";
import type { GitHubProfile, RepositorySummary } from "./types";

export const GitHubService = {
  async getProfile(signal?: AbortSignal): Promise<GitHubProfile> {
    if (USE_MOCK) {
      await delay(200, signal);
      return mockProfile;
    }
    return request<GitHubProfile>("/github/profile", { signal });
  },

  async listPinned(signal?: AbortSignal): Promise<RepositorySummary[]> {
    if (USE_MOCK) {
      await delay(180, signal);
      return enrichedRepositories().filter((r) => r.isPinned);
    }
    return request<RepositorySummary[]>("/github/pinned", { signal });
  },

  async listRecent(signal?: AbortSignal): Promise<RepositorySummary[]> {
    if (USE_MOCK) {
      await delay(180, signal);
      return enrichedRepositories().slice(0, 4);
    }
    return request<RepositorySummary[]>("/github/recent", { signal });
  },

  async refreshRepositories(signal?: AbortSignal): Promise<{ refreshed: number }> {
    if (USE_MOCK) {
      await delay(600, signal);
      return { refreshed: enrichedRepositories().length };
    }
    return request<{ refreshed: number }>("/github/refresh", { method: "POST", signal });
  },
};
