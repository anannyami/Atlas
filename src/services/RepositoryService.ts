import { USE_MOCK, delay, request } from "./http";
import { enrichedRepositories, repositoryDetail } from "./mock-data";
import type { Page, RepositoryDetail, RepositoryListParams, RepositorySummary } from "./types";

function applyFilters(all: RepositorySummary[], params: RepositoryListParams): RepositorySummary[] {
  let out = all;
  if (params.query) {
    const q = params.query.toLowerCase();
    out = out.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.owner.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        r.topics.some((t) => t.includes(q)),
    );
  }
  if (params.languages?.length) out = out.filter((r) => params.languages!.includes(r.language));
  if (params.owners?.length) out = out.filter((r) => params.owners!.includes(r.owner));
  if (params.visibility?.length) out = out.filter((r) => params.visibility!.includes(r.visibility));
  if (params.includeForks === false) out = out.filter((r) => !r.isFork);
  if (params.includeArchived === false) out = out.filter((r) => !r.isArchived);
  if (params.includeTemplates === false) out = out.filter((r) => !r.isTemplate);
  if (params.onlyStarred) out = out.filter((r) => r.isStarred);
  if (params.onlyPinned) out = out.filter((r) => r.isPinned);
  if (params.updatedWithinDays) {
    const cutoff = Date.now() - params.updatedWithinDays * 86_400_000;
    out = out.filter((r) => new Date(r.lastCommitAt).getTime() > cutoff);
  }
  switch (params.sort) {
    case "stars":
      out = [...out].sort((a, b) => b.stars - a.stars);
      break;
    case "name":
      out = [...out].sort((a, b) => a.name.localeCompare(b.name));
      break;
    case "updated":
    case "recent":
      out = [...out].sort(
        (a, b) => new Date(b.lastCommitAt).getTime() - new Date(a.lastCommitAt).getTime(),
      );
      break;
  }
  return out;
}

export const RepositoryService = {
  async list(params: RepositoryListParams = {}, signal?: AbortSignal): Promise<Page<RepositorySummary>> {
    if (USE_MOCK) {
      await delay(220, signal);
      const filtered = applyFilters(enrichedRepositories(), params);
      const pageSize = params.pageSize ?? 12;
      const start = params.cursor ? Number(params.cursor) : 0;
      const items = filtered.slice(start, start + pageSize);
      const nextCursor = start + pageSize < filtered.length ? String(start + pageSize) : null;
      return { items, nextCursor, total: filtered.length };
    }
    return request<Page<RepositorySummary>>("/repositories", { query: params as never, signal });
  },

  async get(id: string, signal?: AbortSignal): Promise<RepositoryDetail | null> {
    if (USE_MOCK) {
      await delay(240, signal);
      return repositoryDetail(id);
    }
    return request<RepositoryDetail>(`/repositories/${encodeURIComponent(id)}`, { signal });
  },

  async listLanguages(signal?: AbortSignal): Promise<string[]> {
    if (USE_MOCK) {
      await delay(80, signal);
      return Array.from(new Set(enrichedRepositories().map((r) => r.language))).sort();
    }
    return request<string[]>("/repositories/languages", { signal });
  },

  async listOwners(signal?: AbortSignal): Promise<string[]> {
    if (USE_MOCK) {
      await delay(80, signal);
      return Array.from(new Set(enrichedRepositories().map((r) => r.owner))).sort();
    }
    return request<string[]>("/repositories/owners", { signal });
  },
};
