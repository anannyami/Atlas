import { USE_MOCK, delay, request } from "./http";
import { mockSearchResults } from "./mock-data";
import type { SearchHit, SearchKind } from "./types";

export interface SearchParams {
  query: string;
  kinds?: SearchKind[];
  limit?: number;
}

export const SearchService = {
  async search({ query, kinds, limit = 40 }: SearchParams, signal?: AbortSignal): Promise<SearchHit[]> {
    if (USE_MOCK) {
      await delay(140, signal);
      const raw = mockSearchResults(query);
      return (kinds?.length ? raw.filter((r) => kinds.includes(r.kind)) : raw).slice(0, limit);
    }
    return request<SearchHit[]>("/search", { query: { query, kinds, limit }, signal });
  },
};
