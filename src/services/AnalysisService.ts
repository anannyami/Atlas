import { USE_MOCK, delay, request } from "./http";
import {
  mockArchitecture,
  mockDependencies,
  mockInsights,
  mockSelection,
  mockTechStack,
} from "./mock-data";
import type {
  ArchitectureGraph,
  DependencyItem,
  InsightItem,
  SelectionAnalysis,
  TechCategory,
} from "./types";

export const AnalysisService = {
  async architecture(repoId: string, signal?: AbortSignal): Promise<ArchitectureGraph> {
    if (USE_MOCK) {
      await delay(260, signal);
      return mockArchitecture();
    }
    return request<ArchitectureGraph>(`/analysis/${encodeURIComponent(repoId)}/architecture`, { signal });
  },

  async dependencies(repoId: string, signal?: AbortSignal): Promise<DependencyItem[]> {
    if (USE_MOCK) {
      await delay(220, signal);
      return mockDependencies;
    }
    return request<DependencyItem[]>(`/analysis/${encodeURIComponent(repoId)}/dependencies`, { signal });
  },

  async techStack(repoId: string, signal?: AbortSignal): Promise<TechCategory[]> {
    if (USE_MOCK) {
      await delay(200, signal);
      return mockTechStack;
    }
    return request<TechCategory[]>(`/analysis/${encodeURIComponent(repoId)}/tech-stack`, { signal });
  },

  async insights(repoId: string, signal?: AbortSignal): Promise<InsightItem[]> {
    if (USE_MOCK) {
      await delay(220, signal);
      return mockInsights;
    }
    return request<InsightItem[]>(`/analysis/${encodeURIComponent(repoId)}/insights`, { signal });
  },

  async selection(
    repoId: string,
    payload: { label: string; path?: string },
    signal?: AbortSignal,
  ): Promise<SelectionAnalysis> {
    if (USE_MOCK) {
      await delay(160, signal);
      return mockSelection(payload.label, payload.path);
    }
    return request<SelectionAnalysis>(`/analysis/${encodeURIComponent(repoId)}/selection`, {
      method: "POST",
      body: payload,
      signal,
    });
  },
};
