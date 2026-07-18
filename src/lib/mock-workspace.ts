import { featuredRepositories, type Repository } from "./mock-repositories";

export type FileNode = {
  name: string;
  kind: "folder" | "file";
  purpose?: string;
  children?: FileNode[];
  usedBy?: string[];
  complexity?: "Low" | "Medium" | "High";
  recommendation?: string;
  files?: string[];
};

export const fileTree: FileNode = {
  name: "react",
  kind: "folder",
  children: [
    {
      name: "src",
      kind: "folder",
      purpose: "Application source. All runtime code lives here.",
      usedBy: ["Build pipeline", "Test runner"],
      complexity: "Medium",
      recommendation: "Entry point for reading the codebase — start with index.ts.",
      children: [
        {
          name: "components",
          kind: "folder",
          purpose: "Reusable UI primitives and composed views.",
          files: ["Button.tsx", "Dialog.tsx", "Dashboard.tsx"],
          usedBy: ["pages/*", "layouts/*"],
          complexity: "Medium",
          recommendation: "High cohesion — each file owns one visual concern.",
          children: [
            { name: "Button.tsx", kind: "file" },
            { name: "Dialog.tsx", kind: "file" },
            { name: "Dashboard.tsx", kind: "file" },
          ],
        },
        {
          name: "hooks",
          kind: "folder",
          purpose: "Reusable stateful logic — auth, data, layout.",
          files: ["useAuth.ts", "useQuery.ts", "useLayout.ts"],
          usedBy: ["components/*", "pages/*"],
          complexity: "Low",
          recommendation: "Read after components — hooks explain how state flows.",
          children: [
            { name: "useAuth.ts", kind: "file" },
            { name: "useQuery.ts", kind: "file" },
          ],
        },
        {
          name: "services",
          kind: "folder",
          purpose: "All outward communication — HTTP, auth, persistence.",
          files: ["auth.ts", "api.ts", "users.ts"],
          usedBy: ["Dashboard", "Settings", "Profile"],
          complexity: "Low",
          recommendation: "Good separation of concerns. Side effects isolated here.",
          children: [
            { name: "auth.ts", kind: "file" },
            { name: "api.ts", kind: "file" },
            { name: "users.ts", kind: "file" },
          ],
        },
        {
          name: "pages",
          kind: "folder",
          purpose: "Route-level compositions. One file per screen.",
          files: ["Home.tsx", "Login.tsx", "Settings.tsx"],
          usedBy: ["Router"],
          complexity: "Low",
          recommendation: "Read last — pages assemble everything above.",
          children: [
            { name: "Home.tsx", kind: "file" },
            { name: "Login.tsx", kind: "file" },
            { name: "Settings.tsx", kind: "file" },
          ],
        },
        {
          name: "utils",
          kind: "folder",
          purpose: "Pure helpers. No side effects, no framework imports.",
          files: ["cn.ts", "format.ts", "invariant.ts"],
          usedBy: ["Everywhere"],
          complexity: "Low",
          recommendation: "cn() is the most-imported symbol in the tree.",
          children: [
            { name: "cn.ts", kind: "file" },
            { name: "format.ts", kind: "file" },
          ],
        },
        { name: "index.ts", kind: "file", purpose: "Main entry. Boots the app." },
      ],
    },
    {
      name: "config",
      kind: "folder",
      purpose: "Build, lint, and environment configuration.",
      files: ["vite.config.ts", "tsconfig.json"],
      complexity: "Low",
      recommendation: "Skip on first read unless debugging the build.",
      children: [
        { name: "vite.config.ts", kind: "file" },
        { name: "tsconfig.json", kind: "file" },
      ],
    },
    { name: "package.json", kind: "file", purpose: "Manifest. Read second, after README." },
    { name: "README.md", kind: "file", purpose: "Start here. Project intent and setup." },
  ],
};

export type ArchNode = {
  id: string;
  label: string;
  x: number;
  y: number;
  purpose: string;
  connections: string[];
  files: string[];
};

export const archNodes: ArchNode[] = [
  { id: "frontend", label: "Frontend", x: 50, y: 8, purpose: "The React application shell. Bootstraps providers and mounts the router.", connections: ["router"], files: ["src/index.ts", "src/App.tsx"] },
  { id: "router", label: "Router", x: 50, y: 22, purpose: "Maps URLs to page components. Central navigation contract.", connections: ["pages", "auth"], files: ["src/router.ts"] },
  { id: "auth", label: "Authentication", x: 15, y: 35, purpose: "JWT validation and session lifecycle. Guards protected routes.", connections: ["api", "router"], files: ["src/services/auth.ts", "src/middleware.ts"] },
  { id: "pages", label: "Pages", x: 70, y: 35, purpose: "Route-level compositions that assemble smaller pieces.", connections: ["components", "hooks"], files: ["src/pages/*"] },
  { id: "components", label: "Components", x: 85, y: 52, purpose: "Reusable UI primitives and composed views.", connections: ["hooks", "utils"], files: ["src/components/*"] },
  { id: "hooks", label: "Hooks", x: 55, y: 52, purpose: "Stateful logic shared across the tree.", connections: ["services"], files: ["src/hooks/*"] },
  { id: "services", label: "Services", x: 30, y: 68, purpose: "Outward communication — HTTP, auth, persistence.", connections: ["api"], files: ["src/services/*"] },
  { id: "api", label: "API", x: 55, y: 82, purpose: "External data boundary. Every network call passes through here.", connections: ["utils"], files: ["src/services/api.ts"] },
  { id: "utils", label: "Utilities", x: 80, y: 82, purpose: "Pure helpers. Deterministic and dependency-free.", connections: [], files: ["src/utils/*"] },
];

export type DepNode = {
  id: string;
  label: string;
  role: string;
  depends: string[];
};

export const dependencies: DepNode[] = [
  { id: "react", label: "React", role: "UI runtime — component tree and reconciliation.", depends: [] },
  { id: "router", label: "React Router", role: "Client-side navigation on top of React.", depends: ["react"] },
  { id: "query", label: "TanStack Query", role: "Server-state cache. Sits between UI and network.", depends: ["react"] },
  { id: "axios", label: "Axios", role: "HTTP transport. Query calls Axios under the hood.", depends: ["query"] },
  { id: "zod", label: "Zod", role: "Runtime schema validation for API payloads.", depends: ["axios"] },
];

export type TechCategory = {
  name: string;
  items: { name: string; why: string }[];
};

export const techStack: TechCategory[] = [
  { name: "Frontend", items: [
    { name: "React", why: "Declarative UI. The mental model the whole app is written in." },
    { name: "TypeScript", why: "Type safety at boundaries — refactors stay honest." },
    { name: "Tailwind", why: "Utility styling. Keeps design tokens close to markup." },
  ] },
  { name: "State", items: [
    { name: "Zustand", why: "Lightweight client state. Chosen over Redux for its ergonomics." },
    { name: "TanStack Query", why: "Server state — caching, refetching, invalidation." },
  ] },
  { name: "Build", items: [
    { name: "Vite", why: "Fast dev server with native ESM. Replaces Webpack." },
  ] },
  { name: "Testing", items: [
    { name: "Vitest", why: "Vite-native test runner. Shares config with the app." },
  ] },
  { name: "Deployment", items: [
    { name: "Vercel", why: "Edge hosting with preview deployments per branch." },
  ] },
];

export type Observation = {
  id: string;
  title: string;
  detail: string;
  why: string;
};

export const observations: Observation[] = [
  { id: "o1", title: "Authentication begins inside auth.ts", detail: "All JWT handling routes through a single module.", why: "One file to read to understand the entire auth story." },
  { id: "o2", title: "Largest component is Dashboard.tsx", detail: "420 lines — five distinct responsibilities in one file.", why: "A likely candidate for extraction. Splitting improves readability." },
  { id: "o3", title: "Most imported utility is cn()", detail: "Referenced by 84% of components.", why: "A change here ripples widely — read it before touching styles." },
  { id: "o4", title: "README coverage is excellent", detail: "Every top-level folder is described in the README.", why: "Trust the README. It's a reliable map, not marketing." },
  { id: "o5", title: "Components folder has high cohesion", detail: "Each file owns one visual concern with minimal cross-imports.", why: "Safe to read files in isolation — few hidden dependencies." },
];

export type Insight = {
  id: string;
  headline: string;
  detail: string;
  recommendation: string;
};

export const insights: Insight[] = [
  { id: "i1", headline: "Largest component", detail: "Dashboard.tsx is 420 lines with 5 concerns.", recommendation: "Extract Header, Charts, and Sidebar into siblings." },
  { id: "i2", headline: "Duplicate utility functions", detail: "formatDate and toDateStr do the same work in two folders.", recommendation: "Consolidate into utils/date.ts." },
  { id: "i3", headline: "Authentication is well isolated", detail: "Auth code touches only three files.", recommendation: "Preserve this boundary in future changes." },
  { id: "i4", headline: "Test coverage is uneven", detail: "Services are 91% covered. UI is 34%.", recommendation: "Prioritise tests for Dashboard.tsx and Home.tsx." },
];

export const readingOrder = ["README.md", "package.json", "src/index.ts", "src/components", "src/hooks", "src/services", "src/pages"];

export function findRepository(id: string): Repository {
  return featuredRepositories.find((r) => r.id === id) ?? featuredRepositories[0];
}

export type WorkspaceSection =
  | "overview"
  | "explorer"
  | "architecture"
  | "dependencies"
  | "tech"
  | "docs"
  | "insights"
  | "search"
  | "settings";
