import { USE_MOCK, delay, request } from "./http";
import { mockDocuments, mockFileTree } from "./mock-data";
import type { DocDocument, FileContent, FileNode } from "./types";

export const WorkspaceService = {
  async fileTree(repoId: string, signal?: AbortSignal): Promise<FileNode> {
    if (USE_MOCK) {
      await delay(180, signal);
      return mockFileTree();
    }
    return request<FileNode>(`/workspace/${encodeURIComponent(repoId)}/tree`, { signal });
  },

  async fileContent(repoId: string, path: string, signal?: AbortSignal): Promise<FileContent> {
    if (USE_MOCK) {
      await delay(140, signal);
      return {
        path,
        language: path.endsWith(".ts") || path.endsWith(".tsx") ? "typescript" : "text",
        loc: 42,
        content: `// ${path}\nexport const placeholder = true;\n`,
      };
    }
    return request<FileContent>(`/workspace/${encodeURIComponent(repoId)}/file`, {
      query: { path },
      signal,
    });
  },

  async documents(repoId: string, signal?: AbortSignal): Promise<DocDocument[]> {
    if (USE_MOCK) {
      await delay(160, signal);
      return mockDocuments();
    }
    return request<DocDocument[]>(`/workspace/${encodeURIComponent(repoId)}/docs`, { signal });
  },
};
