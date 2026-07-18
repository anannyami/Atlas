// Extended mock data for the service layer.
// Deterministic: seeded arrays used by mock adapters until FastAPI is wired.

import { featuredRepositories, continueRepos } from "@/lib/mock-repositories";
import type {
  DependencyItem,
  DocDocument,
  FileNode,
  GitHubProfile,
  InsightItem,
  RepositoryDetail,
  RepositorySummary,
  SearchHit,
  TechCategory,
  ArchitectureGraph,
  SelectionAnalysis,
} from "./types";

const LANGUAGE_COLORS: Record<string, string> = {
  JavaScript: "#F1E05A",
  TypeScript: "#3178C6",
  "C++": "#F34B7D",
  Go: "#00ADD8",
  Python: "#3572A5",
  Rust: "#DEA584",
  Java: "#B07219",
  Ruby: "#701516",
  Swift: "#FFAC45",
  Kotlin: "#A97BFF",
};

function seededRandom(seed: string) {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h ^= h << 13;
    h ^= h >>> 17;
    h ^= h << 5;
    return ((h >>> 0) % 10_000) / 10_000;
  };
}

export function enrichedRepositories(): RepositorySummary[] {
  return featuredRepositories.map((r): RepositorySummary => {
    const rand = seededRandom(r.id);
    const stars = Math.round(rand() * 200_000 + 5_000);
    const languageColor = LANGUAGE_COLORS[r.language] ?? "#C7886B";
    const isPinned = continueRepos.some((c) => c.id === r.id);
    return {
      id: r.id,
      name: r.name,
      owner: r.owner,
      ownerAvatarUrl: `https://avatars.githubusercontent.com/${r.owner}?s=80`,
      description: r.description,
      language: r.language,
      languageColor,
      stars,
      forks: Math.round(stars * (0.08 + rand() * 0.1)),
      watchers: Math.round(stars * (0.02 + rand() * 0.03)),
      openIssues: Math.round(rand() * 900 + 50),
      size: r.size,
      defaultBranch: rand() > 0.3 ? "main" : "master",
      license: ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"][Math.floor(rand() * 4)],
      topics: [r.framework.toLowerCase(), r.language.toLowerCase(), "open-source", r.owner]
        .map((t) => t.replace(/\s+/g, "-"))
        .slice(0, 4),
      lastCommitAt: new Date(Date.now() - rand() * 7 * 86_400_000).toISOString(),
      visibility: "public",
      isFork: false,
      isArchived: false,
      isTemplate: false,
      isStarred: rand() > 0.6,
      isPinned,
      health:
        rand() > 0.75 ? "excellent" : rand() > 0.4 ? "healthy" : rand() > 0.2 ? "fair" : "at-risk",
      healthScore: Math.round(60 + rand() * 40),
      architectureScore: Math.round(55 + rand() * 45),
      complexityScore: Math.round(30 + rand() * 60),
      documentationScore: Math.round(40 + rand() * 55),
      estimatedAnalysisMinutes: Math.round(3 + rand() * 22),
      glyph: r.glyph,
      accent: r.accent,
      framework: r.framework,
      technologies: r.technologies,
      files: r.files,
      folders: r.folders,
      architecture: r.architecture,
      difficulty: r.difficulty,
      estimatedTime: r.estimatedTime,
    };
  });
}

export function repositoryDetail(id: string): RepositoryDetail | null {
  const summary = enrichedRepositories().find((r) => r.id === id);
  if (!summary) return null;
  const rand = seededRandom(`${id}:detail`);
  const languages: RepositoryDetail["languageBreakdown"] = summary.technologies
    .slice(0, 5)
    .map((t, i) => ({
      name: t,
      percent: 0,
      color: Object.values(LANGUAGE_COLORS)[i % Object.values(LANGUAGE_COLORS).length],
    }));
  const raw = languages.map(() => 10 + rand() * 60);
  const sum = raw.reduce((a, b) => a + b, 0);
  languages.forEach((l, i) => (l.percent = Math.round((raw[i] / sum) * 100)));

  return {
    ...summary,
    readme: `# ${summary.owner}/${summary.name}\n\n${summary.description}\n\n## Getting started\n\n\`\`\`bash\ngit clone https://github.com/${summary.owner}/${summary.name}.git\ncd ${summary.name}\nnpm install\n\`\`\`\n\n## Architecture\n\n${summary.architecture}. Read the [Overview](#overview) to see how the pieces fit together.\n\n### Highlights\n\n- Battle-tested at scale\n- Actively maintained\n- Rich ecosystem of plugins\n`,
    latestCommit: {
      sha: Math.random().toString(36).slice(2, 9),
      message: "chore: bump dependencies and refresh lockfile",
      author: summary.owner,
      at: summary.lastCommitAt,
    },
    latestRelease: {
      tag: `v${Math.floor(rand() * 40)}.${Math.floor(rand() * 12)}.${Math.floor(rand() * 20)}`,
      publishedAt: new Date(Date.now() - rand() * 30 * 86_400_000).toISOString(),
    },
    contributors: Array.from({ length: 6 }).map((_, i) => ({
      login: `${summary.owner}-dev-${i + 1}`,
      avatarUrl: `https://avatars.githubusercontent.com/u/${1000 + i}?v=4`,
      contributions: Math.round(200 + rand() * 4000),
    })),
    languageBreakdown: languages,
    commitActivity: Array.from({ length: 26 }).map((_, i) => ({
      week: `w${i + 1}`,
      commits: Math.round(4 + rand() * 60),
    })),
    timeline: [
      { at: "3 days ago", kind: "release", text: "Published patch release" },
      { at: "1 week ago", kind: "commit", text: "Refactored router internals" },
      { at: "2 weeks ago", kind: "issue", text: "Closed 14 stale issues" },
      { at: "1 month ago", kind: "release", text: "Minor version shipped" },
    ],
    scores: {
      maturity: Math.round(70 + rand() * 28),
      health: summary.healthScore,
      documentation: summary.documentationScore,
      architecture: summary.architectureScore,
      maintainability: Math.round(60 + rand() * 35),
    },
    estimatedOnboardingHours: Math.round(2 + rand() * 10),
    estimatedBuildMinutes: Math.round(1 + rand() * 12),
  };
}

export const mockProfile: GitHubProfile = {
  id: "u_atlas_1",
  login: "atlas-explorer",
  name: "Atlas Explorer",
  bio: "Reading unfamiliar codebases for a living. Building Atlas.",
  avatarUrl: "https://avatars.githubusercontent.com/u/9919?v=4",
  htmlUrl: "https://github.com/atlas-explorer",
  followers: 1284,
  following: 96,
  publicRepos: 42,
  privateRepos: 17,
  organizations: [
    { login: "atlas-labs", name: "Atlas Labs", avatarUrl: "https://avatars.githubusercontent.com/u/1?v=4" },
    { login: "open-source", name: "Open Source", avatarUrl: "https://avatars.githubusercontent.com/u/2?v=4" },
    { login: "readable-code", name: "Readable Code", avatarUrl: "https://avatars.githubusercontent.com/u/3?v=4" },
  ],
  createdAt: "2016-04-11T09:12:00.000Z",
};

export const mockDependencies: DependencyItem[] = [
  {
    id: "react",
    name: "react",
    group: "frontend",
    currentVersion: "19.0.0",
    latestVersion: "19.0.0",
    outdated: false,
    hasSecurityAdvisory: false,
    popularity: 99,
    homepage: "https://react.dev",
    repository: "https://github.com/facebook/react",
    license: "MIT",
    sizeKb: 42,
    dependencies: 1,
    dependents: 8_400_000,
    description: "The library for web and native user interfaces.",
  },
  {
    id: "vite",
    name: "vite",
    group: "build",
    currentVersion: "7.0.1",
    latestVersion: "7.0.3",
    outdated: true,
    hasSecurityAdvisory: false,
    popularity: 96,
    homepage: "https://vitejs.dev",
    repository: "https://github.com/vitejs/vite",
    license: "MIT",
    sizeKb: 1_200,
    dependencies: 12,
    dependents: 1_200_000,
    description: "Next generation frontend tooling.",
  },
  {
    id: "vitest",
    name: "vitest",
    group: "testing",
    currentVersion: "2.1.4",
    latestVersion: "2.1.4",
    outdated: false,
    hasSecurityAdvisory: false,
    popularity: 88,
    homepage: "https://vitest.dev",
    repository: "https://github.com/vitest-dev/vitest",
    license: "MIT",
    sizeKb: 800,
    dependencies: 8,
    dependents: 320_000,
    description: "Blazing fast unit test framework.",
  },
  {
    id: "fastapi",
    name: "fastapi",
    group: "backend",
    currentVersion: "0.115.0",
    latestVersion: "0.116.1",
    outdated: true,
    hasSecurityAdvisory: false,
    popularity: 92,
    homepage: "https://fastapi.tiangolo.com",
    repository: "https://github.com/tiangolo/fastapi",
    license: "MIT",
    sizeKb: 480,
    dependencies: 3,
    dependents: 240_000,
    description: "Modern, fast web framework for Python APIs.",
  },
  {
    id: "postgres",
    name: "postgres",
    group: "infrastructure",
    currentVersion: "16.4",
    latestVersion: "16.4",
    outdated: false,
    hasSecurityAdvisory: false,
    popularity: 95,
    homepage: "https://www.postgresql.org",
    repository: null,
    license: "PostgreSQL",
    sizeKb: 220_000,
    dependencies: 0,
    dependents: 0,
    description: "The world's most advanced open source database.",
  },
  {
    id: "eslint",
    name: "eslint",
    group: "dev",
    currentVersion: "9.11.0",
    latestVersion: "9.14.0",
    outdated: true,
    hasSecurityAdvisory: false,
    popularity: 94,
    homepage: "https://eslint.org",
    repository: "https://github.com/eslint/eslint",
    license: "MIT",
    sizeKb: 640,
    dependencies: 26,
    dependents: 6_800_000,
    description: "Pluggable JavaScript linter.",
  },
  {
    id: "openssl",
    name: "openssl",
    group: "infrastructure",
    currentVersion: "3.0.11",
    latestVersion: "3.2.1",
    outdated: true,
    hasSecurityAdvisory: true,
    popularity: 90,
    homepage: "https://www.openssl.org",
    repository: null,
    license: "Apache-2.0",
    sizeKb: 5_200,
    dependencies: 0,
    dependents: 0,
    description: "TLS/SSL and crypto library.",
  },
];

export const mockTechStack: TechCategory[] = [
  {
    name: "Frontend",
    items: [
      { name: "React", version: "19.0.0", purpose: "UI library", usedInFiles: ["src/routes/", "src/components/"], popularity: 99, docsUrl: "https://react.dev", icon: "react" },
      { name: "TanStack Router", version: "1.x", purpose: "Type-safe file routing", usedInFiles: ["src/routes/"], popularity: 84, docsUrl: "https://tanstack.com/router", icon: "router" },
    ],
  },
  {
    name: "Styling",
    items: [
      { name: "Tailwind CSS", version: "4.x", purpose: "Utility-first styling", usedInFiles: ["src/styles.css", "src/components/"], popularity: 96, docsUrl: "https://tailwindcss.com", icon: "tailwind" },
      { name: "Motion", version: "12.x", purpose: "Animations", usedInFiles: ["src/components/", "src/routes/"], popularity: 78, docsUrl: "https://motion.dev", icon: "motion" },
    ],
  },
  {
    name: "State Management",
    items: [
      { name: "React state + context", version: "19.0.0", purpose: "Local + shared state", usedInFiles: ["src/hooks/", "src/routes/"], popularity: 92, docsUrl: "https://react.dev/learn/managing-state", icon: "react" },
    ],
  },
  {
    name: "Backend",
    items: [
      { name: "FastAPI", version: "0.116.1", purpose: "REST API", usedInFiles: ["backend/app/"], popularity: 92, docsUrl: "https://fastapi.tiangolo.com", icon: "fastapi" },
    ],
  },
  {
    name: "Database",
    items: [
      { name: "PostgreSQL", version: "16.4", purpose: "Primary datastore", usedInFiles: ["backend/db/"], popularity: 95, docsUrl: "https://www.postgresql.org", icon: "postgres" },
    ],
  },
  {
    name: "Authentication",
    items: [
      { name: "GitHub OAuth", version: "—", purpose: "Sign-in and repo access", usedInFiles: ["src/services/AuthService.ts"], popularity: 90, docsUrl: "https://docs.github.com/en/apps/oauth-apps", icon: "github" },
    ],
  },
  {
    name: "Testing",
    items: [
      { name: "Vitest", version: "2.1.4", purpose: "Unit tests", usedInFiles: ["**/*.test.ts"], popularity: 88, docsUrl: "https://vitest.dev", icon: "vitest" },
      { name: "Playwright", version: "1.48", purpose: "End-to-end tests", usedInFiles: ["tests/e2e/"], popularity: 84, docsUrl: "https://playwright.dev", icon: "playwright" },
    ],
  },
  {
    name: "CI/CD",
    items: [
      { name: "GitHub Actions", version: "—", purpose: "Pipelines", usedInFiles: [".github/workflows/"], popularity: 92, docsUrl: "https://docs.github.com/actions", icon: "github" },
    ],
  },
  {
    name: "Containerization",
    items: [
      { name: "Docker", version: "27.x", purpose: "Runtime container", usedInFiles: ["Dockerfile", "docker-compose.yml"], popularity: 93, docsUrl: "https://docs.docker.com", icon: "docker" },
    ],
  },
  {
    name: "Infrastructure",
    items: [
      { name: "Nginx", version: "1.27", purpose: "Reverse proxy", usedInFiles: ["infra/nginx.conf"], popularity: 89, docsUrl: "https://nginx.org", icon: "nginx" },
    ],
  },
  {
    name: "Cloud",
    items: [
      { name: "Cloudflare Workers", version: "—", purpose: "Edge runtime", usedInFiles: ["src/server.ts"], popularity: 82, docsUrl: "https://developers.cloudflare.com/workers", icon: "cloudflare" },
    ],
  },
  {
    name: "Build Tools",
    items: [
      { name: "Vite", version: "7.0.1", purpose: "Bundler & dev server", usedInFiles: ["vite.config.ts"], popularity: 96, docsUrl: "https://vitejs.dev", icon: "vite" },
    ],
  },
  {
    name: "Package Managers",
    items: [
      { name: "Bun", version: "1.1", purpose: "Package manager", usedInFiles: ["bun.lockb"], popularity: 78, docsUrl: "https://bun.sh", icon: "bun" },
    ],
  },
  {
    name: "Developer Tools",
    items: [
      { name: "ESLint", version: "9.11.0", purpose: "Linting", usedInFiles: ["eslint.config.js"], popularity: 94, docsUrl: "https://eslint.org", icon: "eslint" },
      { name: "Prettier", version: "3.3", purpose: "Formatting", usedInFiles: [".prettierrc"], popularity: 92, docsUrl: "https://prettier.io", icon: "prettier" },
    ],
  },
];

export const mockInsights: InsightItem[] = [
  {
    id: "ins-cyclic",
    category: "circular-dependency",
    severity: "high",
    title: "Circular import between routes and services",
    description: "`src/routes/index.tsx` imports from `src/services/AuthService.ts`, which re-imports a helper that reaches back into routes.",
    affectedFiles: ["src/routes/index.tsx", "src/services/AuthService.ts"],
    reason: "Circular imports slow cold starts and confuse tree-shaking.",
    suggestedFix: "Extract the shared helper into `src/lib/session.ts` so both sides depend on a leaf module.",
  },
  {
    id: "ins-large",
    category: "large-file",
    severity: "medium",
    title: "Overview panel exceeds 500 lines",
    description: "The Overview panel is doing too much: layout, data shaping, and analytics all live together.",
    affectedFiles: ["src/components/workspace/repository/panels/OverviewPanel.tsx"],
    reason: "Files above 400 lines are harder to review and easier to break during refactors.",
    suggestedFix: "Split into `OverviewHeader`, `OverviewStats`, and `OverviewTimeline` components.",
  },
  {
    id: "ins-nesting",
    category: "deep-nesting",
    severity: "low",
    title: "Deep folder nesting in components",
    description: "`components/workspace/repository/panels/…` reaches 5 levels of nesting.",
    affectedFiles: ["src/components/workspace/repository/panels/"],
    reason: "Deep paths make imports noisy and encourage duplication.",
    suggestedFix: "Flatten to `components/workspace/panels/…` and use file naming for grouping.",
  },
  {
    id: "ins-unused",
    category: "unused-code",
    severity: "low",
    title: "Two exported helpers are never imported",
    description: "`initials` in `lib/auth.ts` and `readingOrder` in `mock-workspace.ts` have no callers outside their own files.",
    affectedFiles: ["src/lib/auth.ts", "src/lib/mock-workspace.ts"],
    reason: "Dead exports mislead consumers and pad the bundle.",
    suggestedFix: "Delete them or wire them into the components that were originally planned to use them.",
  },
  {
    id: "ins-security",
    category: "security-risk",
    severity: "high",
    title: "openssl 3.0.11 has known advisories",
    description: "Base image ships with an OpenSSL version affected by CVE-2023-5678.",
    affectedFiles: ["Dockerfile"],
    reason: "Runtime crypto library must be current to receive security patches.",
    suggestedFix: "Bump base image to a variant carrying openssl >= 3.2.1.",
  },
  {
    id: "ins-docs",
    category: "missing-documentation",
    severity: "medium",
    title: "Public services have no JSDoc",
    description: "None of the exports in `src/services/*` document their parameters or return shape.",
    affectedFiles: ["src/services/RepositoryService.ts", "src/services/AnalysisService.ts"],
    reason: "Editor tooltips fall back to raw types; onboarding suffers.",
    suggestedFix: "Add a one-line JSDoc summary per exported function; leave complex types to the DTO.",
  },
  {
    id: "ins-a11y",
    category: "accessibility",
    severity: "medium",
    title: "Icon-only buttons missing labels",
    description: "Several toolbar buttons render only an icon without an `aria-label`.",
    affectedFiles: ["src/components/workspace/repository/WorkspaceTopBar.tsx"],
    reason: "Screen readers announce nothing for these controls.",
    suggestedFix: "Add `aria-label` describing the action for every icon-only button.",
  },
];

export function mockArchitecture(): ArchitectureGraph {
  return {
    clusters: [
      { id: "ui", label: "UI", color: "#C7886B" },
      { id: "state", label: "State", color: "#B1705F" },
      { id: "services", label: "Services", color: "#792E3C" },
      { id: "infra", label: "Infrastructure", color: "#5C1E2A" },
    ],
    nodes: [
      { id: "root", label: "repository", kind: "repository", cluster: "ui", purpose: "Entry", files: ["package.json"], complexity: "Low", loc: 40 },
      { id: "routes", label: "routes/", kind: "folder", cluster: "ui", purpose: "Top-level pages", files: ["src/routes/"], complexity: "Moderate", loc: 800 },
      { id: "components", label: "components/", kind: "folder", cluster: "ui", purpose: "Reusable UI", files: ["src/components/"], complexity: "Moderate", loc: 1400 },
      { id: "hooks", label: "useAuth", kind: "hook", cluster: "state", purpose: "Session hook", files: ["src/lib/auth.ts"], complexity: "Low", loc: 80 },
      { id: "services", label: "services/", kind: "package", cluster: "services", purpose: "Typed API", files: ["src/services/"], complexity: "Moderate", loc: 700 },
      { id: "api", label: "FastAPI", kind: "api", cluster: "services", purpose: "Backend", files: ["backend/app/"], complexity: "High", loc: 3500 },
      { id: "db", label: "PostgreSQL", kind: "database", cluster: "infra", purpose: "Datastore", files: [], complexity: "Moderate", loc: 0 },
      { id: "config", label: "vite.config", kind: "configuration", cluster: "infra", purpose: "Build config", files: ["vite.config.ts"], complexity: "Low", loc: 60 },
    ],
    edges: [
      { from: "root", to: "routes", kind: "imports", weight: 1 },
      { from: "root", to: "components", kind: "imports", weight: 1 },
      { from: "routes", to: "components", kind: "renders", weight: 3 },
      { from: "routes", to: "hooks", kind: "calls", weight: 2 },
      { from: "components", to: "hooks", kind: "calls", weight: 2 },
      { from: "hooks", to: "services", kind: "calls", weight: 2 },
      { from: "services", to: "api", kind: "calls", weight: 3 },
      { from: "api", to: "db", kind: "reads", weight: 4 },
      { from: "root", to: "config", kind: "imports", weight: 1 },
    ],
  };
}

export function mockFileTree(): FileNode {
  return {
    path: "/",
    name: "repository",
    kind: "folder",
    size: 0,
    children: [
      {
        path: "/src",
        name: "src",
        kind: "folder",
        size: 0,
        children: [
          {
            path: "/src/routes",
            name: "routes",
            kind: "folder",
            size: 0,
            children: [
              { path: "/src/routes/index.tsx", name: "index.tsx", kind: "route", size: 4_200, loc: 120, language: "tsx" },
              { path: "/src/routes/auth.tsx", name: "auth.tsx", kind: "route", size: 12_400, loc: 320, language: "tsx" },
              { path: "/src/routes/explore.tsx", name: "explore.tsx", kind: "route", size: 8_800, loc: 240, language: "tsx" },
            ],
          },
          {
            path: "/src/services",
            name: "services",
            kind: "folder",
            size: 0,
            children: [
              { path: "/src/services/http.ts", name: "http.ts", kind: "file", size: 4_800, loc: 160, language: "ts" },
              { path: "/src/services/types.ts", name: "types.ts", kind: "file", size: 5_600, loc: 210, language: "ts" },
              { path: "/src/services/AuthService.ts", name: "AuthService.ts", kind: "file", size: 2_200, loc: 90, language: "ts" },
            ],
          },
        ],
      },
      { path: "/README.md", name: "README.md", kind: "doc", size: 3_200, loc: 100, language: "md" },
      { path: "/package.json", name: "package.json", kind: "config", size: 1_100, loc: 45, language: "json" },
    ],
  };
}

export function mockDocuments(): DocDocument[] {
  return [
    {
      path: "README.md",
      title: "README",
      markdown: `# Atlas\n\n**Atlas** is a repository intelligence platform.\n\n## Features\n\n- Architecture visualization\n- Dependency analysis\n- Documentation explorer\n- Insights & health\n\n## Getting Started\n\n\`\`\`bash\nbun install\nbun dev\n\`\`\`\n\n> Read the [Architecture](architecture.md) doc next.`,
    },
    {
      path: "docs/architecture.md",
      title: "Architecture",
      markdown: `# Architecture\n\nAtlas is composed of a React frontend and a FastAPI backend.\n\n| Layer | Responsibility |\n| --- | --- |\n| UI | Routes, panels, visualizations |\n| Services | Typed API calls |\n| Backend | Analysis pipeline |\n\n## Data flow\n\n1. User signs in with GitHub.\n2. Backend clones the repository and analyzes it.\n3. Frontend renders the report.`,
    },
    {
      path: "docs/contributing.md",
      title: "Contributing",
      markdown: `# Contributing\n\n- [x] Fork the repository\n- [x] Create a feature branch\n- [ ] Open a pull request\n\nPlease follow the [Code of Conduct](conduct.md).`,
    },
  ];
}

export function mockSearchResults(query: string): SearchHit[] {
  const q = query.toLowerCase().trim();
  const seed: SearchHit[] = [
    { id: "s1", kind: "file", label: "AuthService.ts", path: "src/services/AuthService.ts", context: "export async function signIn(...)" },
    { id: "s2", kind: "component", label: "RepositoryCard", path: "src/components/workspace/RepositoryCard.tsx", context: "Renders a repository summary card" },
    { id: "s3", kind: "hook", label: "useAuth", path: "src/lib/auth.ts", context: "Returns { user, isAuthenticated, disconnect }" },
    { id: "s4", kind: "function", label: "signInWithGitHub", path: "src/lib/auth.ts", context: "Simulates the GitHub OAuth round-trip" },
    { id: "s5", kind: "route", label: "/auth", path: "src/routes/auth.tsx", context: "Sign in with GitHub" },
    { id: "s6", kind: "interface", label: "RepositoryDetail", path: "src/services/types.ts", context: "extends RepositorySummary" },
    { id: "s7", kind: "constant", label: "LANGUAGE_COLORS", path: "src/services/mock-data.ts", context: "Record<string, string>" },
    { id: "s8", kind: "configuration", label: "vite.config.ts", path: "vite.config.ts", context: "TanStack Start plugin" },
  ];
  if (!q) return seed;
  return seed.filter((s) => s.label.toLowerCase().includes(q) || s.context.toLowerCase().includes(q));
}

export function mockSelection(label: string, path?: string): SelectionAnalysis {
  const rand = seededRandom(label + (path ?? ""));
  return {
    summary: `${label} is part of the workspace's active surface. It has been read by 4 collaborators in the last week.`,
    purpose: `Owns the ${label} responsibility. Bridges its cluster to the rest of the graph.`,
    filePath: path ?? null,
    complexity: (["Low", "Moderate", "High", "Very High"] as const)[Math.floor(rand() * 4)],
    dependencies: ["react", "motion", "@/services/http"],
    dependents: ["OverviewPanel", "RepositoryCard"],
    linesOfCode: Math.round(80 + rand() * 400),
    documentation: "Basic docblock present. Consider expanding with an example.",
    recentChanges: [
      { at: "2 days ago", text: "Refactored to use typed services" },
      { at: "1 week ago", text: "Extracted animation to a hook" },
    ],
    riskScore: Math.round(rand() * 60),
    ownership: [
      { login: "atlas-explorer", avatarUrl: "https://avatars.githubusercontent.com/u/9919?v=4", contributions: 42 },
      { login: "atlas-labs-dev", avatarUrl: "https://avatars.githubusercontent.com/u/9920?v=4", contributions: 17 },
    ],
    recommendations: [
      "Read the referenced files before making changes.",
      "Add a unit test that captures the current behaviour.",
      "Bump documentation to describe the returned shape.",
    ],
  };
}
