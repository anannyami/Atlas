import { request } from "./http";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  question: string;
  analysis: Record<string, unknown>;
  conversation?: ChatMessage[];
}

export interface ChatSource {
  title: string;
  kind: string;
  snippet: string;
}

export interface ResponseValidationResult {
  passed: boolean;
  overall_score: number;
  word_count: number;
  missing_sections: string[];
  missing_repository_evidence: string[];
  missing_engineering_observations: string[];
  generic_reasoning: boolean;
  hallucination_risk: number;
  followup_continuity: number;
  issues: string[];
  category_scores: Record<string, number>;
  evidence_matches: string[];
  synthesized_areas: string[];
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  validation: ResponseValidationResult | null;
}

export const AtlasChatService = {
  async ask(payload: ChatRequest): Promise<ChatResponse> {
    return request<ChatResponse>("/chat", {
      method: "POST",
      body: payload,
      timeoutMs: 250_000,
      retries: 0,
    });
  },
};
