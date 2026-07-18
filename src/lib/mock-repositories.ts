export type Difficulty = "Beginner" | "Intermediate" | "Advanced" | "Expert";

export type Repository = {
  id: string;
  name: string;
  owner: string;
  description: string;
  language: string;
  framework: string;
  size: string;
  files: number;
  folders: number;
  stars: string;
  difficulty: Difficulty;
  architecture: string;
  estimatedTime: string;
  technologies: string[];
  accent: [string, string]; // gradient stops
  glyph: "atom" | "triangle" | "square" | "brain" | "hex" | "node" | "bolt";
};

export const featuredRepositories: Repository[] = [
  {
    id: "facebook-react",
    name: "react",
    owner: "facebook",
    description:
      "The library for web and native user interfaces. A declarative, component-based runtime that reshaped how the web is written.",
    language: "JavaScript",
    framework: "React Core",
    size: "412 MB",
    files: 6842,
    folders: 341,
    stars: "228k",
    difficulty: "Advanced",
    architecture: "Monorepo · Reconciler + Fiber",
    estimatedTime: "6–8 hours",
    technologies: ["React", "Flow", "Rollup", "Jest", "Node.js"],
    accent: ["#C7886B", "#792E3C"],
    glyph: "atom",
  },
  {
    id: "vercel-next",
    name: "next.js",
    owner: "vercel",
    description:
      "The React framework for the web. A full-stack runtime with hybrid rendering, edge routing, and a compiler built for scale.",
    language: "TypeScript",
    framework: "Next.js",
    size: "1.2 GB",
    files: 12480,
    folders: 892,
    stars: "132k",
    difficulty: "Advanced",
    architecture: "Turborepo · App Router + SWC",
    estimatedTime: "8–10 hours",
    technologies: ["TypeScript", "React", "Rust", "Turbopack"],
    accent: ["#B1705F", "#5C1E2A"],
    glyph: "triangle",
  },
  {
    id: "microsoft-vscode",
    name: "vscode",
    owner: "microsoft",
    description:
      "The editor that runs everywhere. A layered TypeScript codebase spanning Electron, the extension host, and a language protocol.",
    language: "TypeScript",
    framework: "Electron",
    size: "2.8 GB",
    files: 24310,
    folders: 1_412,
    stars: "168k",
    difficulty: "Expert",
    architecture: "Layered · Main / Renderer / Extension host",
    estimatedTime: "12+ hours",
    technologies: ["TypeScript", "Electron", "Node.js", "Monaco"],
    accent: ["#D5A57E", "#8E3E4D"],
    glyph: "square",
  },
  {
    id: "tensorflow-tensorflow",
    name: "tensorflow",
    owner: "tensorflow",
    description:
      "An end-to-end platform for machine learning. Graph execution, gradient tape, and a kernel dispatch spanning CPU, GPU and TPU.",
    language: "C++",
    framework: "TensorFlow",
    size: "3.6 GB",
    files: 31840,
    folders: 2210,
    stars: "186k",
    difficulty: "Expert",
    architecture: "Layered · Bazel + XLA compiler",
    estimatedTime: "12+ hours",
    technologies: ["C++", "Python", "CUDA", "Bazel", "XLA"],
    accent: ["#E5C89B", "#9E4B50"],
    glyph: "brain",
  },
  {
    id: "kubernetes-kubernetes",
    name: "kubernetes",
    owner: "kubernetes",
    description:
      "Production-grade container orchestration. Controllers, informers, and a declarative API that made distributed systems mainstream.",
    language: "Go",
    framework: "Kubernetes",
    size: "1.9 GB",
    files: 22540,
    folders: 1830,
    stars: "108k",
    difficulty: "Expert",
    architecture: "Microservices · Control plane + kubelets",
    estimatedTime: "10–12 hours",
    technologies: ["Go", "gRPC", "etcd", "Protobuf"],
    accent: ["#C7886B", "#5C1E2A"],
    glyph: "hex",
  },
  {
    id: "nodejs-node",
    name: "node",
    owner: "nodejs",
    description:
      "The JavaScript runtime built on V8. Event loop, libuv, and a native bridge that carries most of the modern web.",
    language: "C++",
    framework: "Node.js",
    size: "1.1 GB",
    files: 9820,
    folders: 612,
    stars: "104k",
    difficulty: "Advanced",
    architecture: "Layered · V8 + libuv event loop",
    estimatedTime: "8–10 hours",
    technologies: ["C++", "JavaScript", "libuv", "V8"],
    accent: ["#B1705F", "#792E3C"],
    glyph: "node",
  },
  {
    id: "expressjs-express",
    name: "express",
    owner: "expressjs",
    description:
      "Fast, minimalist web framework for Node.js. A small routing core that still powers a generation of backends.",
    language: "JavaScript",
    framework: "Express",
    size: "3.2 MB",
    files: 128,
    folders: 18,
    stars: "64k",
    difficulty: "Beginner",
    architecture: "Middleware pipeline · Router + Layer",
    estimatedTime: "1–2 hours",
    technologies: ["JavaScript", "Node.js", "HTTP"],
    accent: ["#F0E6B1", "#B1705F"],
    glyph: "bolt",
  },
];

export type RecentRepo = {
  id: string;
  name: string;
  owner: string;
  lastOpened: string;
  architecturePct: number;
  documentationPct: number;
  insights: number;
  accent: [string, string];
};

export const continueRepos: RecentRepo[] = [
  {
    id: "facebook-react",
    name: "react",
    owner: "facebook",
    lastOpened: "2 hours ago",
    architecturePct: 62,
    documentationPct: 48,
    insights: 14,
    accent: ["#C7886B", "#792E3C"],
  },
  {
    id: "vercel-next",
    name: "next.js",
    owner: "vercel",
    lastOpened: "Yesterday",
    architecturePct: 34,
    documentationPct: 21,
    insights: 7,
    accent: ["#B1705F", "#5C1E2A"],
  },
  {
    id: "nodejs-node",
    name: "node",
    owner: "nodejs",
    lastOpened: "3 days ago",
    architecturePct: 88,
    documentationPct: 74,
    insights: 22,
    accent: ["#B1705F", "#792E3C"],
  },
];

export type Activity = {
  id: string;
  kind: "opened" | "generated" | "viewed" | "searched" | "pinned";
  title: string;
  context: string;
  time: string;
};

export const recentActivity: Activity[] = [
  { id: "a1", kind: "opened",    title: "Opened react",                 context: "facebook/react",  time: "2h ago" },
  { id: "a2", kind: "generated", title: "Generated documentation",       context: "packages/react-reconciler", time: "2h ago" },
  { id: "a3", kind: "viewed",    title: "Viewed architecture map",       context: "vercel/next.js",  time: "Yesterday" },
  { id: "a4", kind: "searched",  title: "Searched for “authentication”", context: "nodejs/node",     time: "2 days ago" },
  { id: "a5", kind: "pinned",    title: "Pinned /src/api",               context: "expressjs/express", time: "3 days ago" },
];

export type AnalyzedRepo = { id: string; url: string; name: string; when: string };

export const recentlyAnalyzed: AnalyzedRepo[] = [
  { id: "r1", url: "github.com/tanstack/router",     name: "tanstack/router",     when: "Today" },
  { id: "r2", url: "github.com/shadcn-ui/ui",        name: "shadcn-ui/ui",        when: "Yesterday" },
  { id: "r3", url: "github.com/vitejs/vite",         name: "vitejs/vite",         when: "3 days ago" },
];

