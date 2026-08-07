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

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

export const AtlasChatService = {
  async ask(payload: ChatRequest): Promise<ChatResponse> {
    return request<ChatResponse>("/chat", {
      method: "POST",
      body: payload,
    });
  },
};
