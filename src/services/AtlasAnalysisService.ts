import { request } from "./http";

import type { AnalysisResponse } from "@/types/atlas";

export interface AnalyzeRepositoryRequest {
  repo_url: string;
}

interface AnalyzeRepositoryApiResponse {
  success: boolean;
  data: AnalysisResponse;
}

export const AtlasAnalysisService = {
  async analyzeRepository(repoUrl: string, signal?: AbortSignal): Promise<AnalysisResponse> {
    const response = await request<AnalysisResponse>("/analyze", {
      method: "POST",
      body: {
        repo_url: repoUrl,
      },
      signal,
    });

    return response;
  },
};
