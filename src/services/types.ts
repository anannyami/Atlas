// Typed DTOs for the Atlas API contract.
// Mirrors the FastAPI backend that will replace the mock adapter.

export type Visibility = "public" | "private" | "internal";
export type Severity = "low" | "medium" | "high" | "critical";

export interface GitHubOrg {
  login: string;
  name: string;
  avatarUrl: string;
}

export interface GitHubProfile {
  id: string;
  login: string;
  name: string;
  bio: string | null;
  avatarUrl: string;
  htmlUrl: string;
  followers: number;
  following: number;
  publicRepos: number;
  privateRepos: number;
  organizations: GitHubOrg[];
  createdAt: string;
}

export interface AuthSession {
  token: string;
  expiresAt: number; // epoch ms
  profile: GitHubProfile;
}

export type AuthStage =
  | "connecting"
  | "redirecting"
  | "authorizing"
  | "fetching_profile"
  | "fetching_repositories"
  | "completed";

export interface AuthProgress {
  stage: AuthStage;
  message: string;
  progress: number; // 0..1
}

export type RepoHealth = "excellent" | "healthy" | "fair" | "at-risk";
export type Complexity = "Low" | "Moderate" | "High" | "Very High";

export interface RepositorySummary {
  id: string;
  name: string;
  owner: string;
  ownerAvatarUrl: string;
  description: string;
  language: string;
  languageColor: string;
  stars: number;
  forks: number;
  watchers: number;
  openIssues: number;
  size: string;
  defaultBranch: string;
  license: string | null;
  topics: string[];
  lastCommitAt: string;
  visibility: Visibility;
  isFork: boolean;
  isArchived: boolean;
  isTemplate: boolean;
  isStarred: boolean;
  isPinned: boolean;
  health: RepoHealth;
  healthScore: number; // 0..100
  architectureScore: number;
  complexityScore: number;
  documentationScore: number;
  estimatedAnalysisMinutes: number;
  // Preserved from legacy mock for the current grid
  glyph: "atom" | "triangle" | "square" | "brain" | "hex" | "node" | "bolt";
  accent: [string, string];
  framework: string;
  technologies: string[];
  files: number;
  folders: number;
  architecture: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced" | "Expert";
  estimatedTime: string;
}

export interface RepositoryListParams {
  query?: string;
  languages?: string[];
  owners?: string[];
  orgs?: string[];
  visibility?: Visibility[];
  includeForks?: boolean;
  includeArchived?: boolean;
  includeTemplates?: boolean;
  updatedWithinDays?: number;
  onlyRecentlyViewed?: boolean;
  onlyStarred?: boolean;
  onlyPinned?: boolean;
  sort?: "recent" | "stars" | "name" | "size" | "updated";
  cursor?: string | null;
  pageSize?: number;
}

export interface Page<T> {
  items: T[];
  nextCursor: string | null;
  total: number;
}

export interface RepositoryDetail extends RepositorySummary {
  readme: string;
  latestCommit: { sha: string; message: string; author: string; at: string };
  latestRelease: { tag: string; publishedAt: string } | null;
  contributors: { login: string; avatarUrl: string; contributions: number }[];
  languageBreakdown: { name: string; percent: number; color: string }[];
  commitActivity: { week: string; commits: number }[];
  timeline: { at: string; kind: string; text: string }[];
  scores: {
    maturity: number;
    health: number;
    documentation: number;
    architecture: number;
    maintainability: number;
  };
  estimatedOnboardingHours: number;
  estimatedBuildMinutes: number;
}

export interface DependencyItem {
  id: string;
  name: string;
  group: "frontend" | "backend" | "dev" | "testing" | "build" | "infrastructure";
  currentVersion: string;
  latestVersion: string;
  outdated: boolean;
  hasSecurityAdvisory: boolean;
  popularity: number; // 0..100
  homepage: string | null;
  repository: string | null;
  license: string | null;
  sizeKb: number;
  dependencies: number;
  dependents: number;
  description: string;
}

export interface TechItem {
  name: string;
  version: string;
  purpose: string;
  usedInFiles: string[];
  popularity: number;
  docsUrl: string;
  icon: string; // slug
}

export interface TechCategory {
  name:
    | "Frontend"
    | "Backend"
    | "Database"
    | "Infrastructure"
    | "Cloud"
    | "Authentication"
    | "Testing"
    | "CI/CD"
    | "Containerization"
    | "State Management"
    | "Styling"
    | "Build Tools"
    | "Package Managers"
    | "Developer Tools";
  items: TechItem[];
}

export interface InsightItem {
  id: string;
  category:
    | "architecture-smell"
    | "circular-dependency"
    | "large-file"
    | "deep-nesting"
    | "unused-code"
    | "duplicate-code"
    | "dead-export"
    | "missing-documentation"
    | "configuration-problem"
    | "security-risk"
    | "performance"
    | "accessibility"
    | "refactoring-suggestion";
  severity: Severity;
  title: string;
  description: string;
  affectedFiles: string[];
  reason: string;
  suggestedFix: string;
}

export interface ArchNode {
  id: string;
  label: string;
  kind:
    | "repository"
    | "folder"
    | "file"
    | "package"
    | "component"
    | "hook"
    | "page"
    | "service"
    | "api"
    | "database"
    | "utility"
    | "configuration";
  cluster: string;
  purpose: string;
  files: string[];
  complexity: Complexity;
  loc: number;
}

export interface ArchEdge {
  from: string;
  to: string;
  kind: "imports" | "renders" | "calls" | "reads" | "writes" | "extends";
  weight: number;
}

export interface ArchitectureGraph {
  nodes: ArchNode[];
  edges: ArchEdge[];
  clusters: { id: string; label: string; color: string }[];
}

export type FileKind =
  | "folder"
  | "file"
  | "component"
  | "hook"
  | "route"
  | "config"
  | "test"
  | "doc";

export interface FileNode {
  path: string;
  name: string;
  kind: FileKind;
  size: number;
  loc?: number;
  children?: FileNode[];
  language?: string;
}

export interface FileContent {
  path: string;
  language: string;
  content: string;
  loc: number;
}

export interface DocDocument {
  path: string;
  title: string;
  markdown: string;
}

export interface DocTree {
  documents: DocDocument[];
}

export type SearchKind =
  | "file"
  | "folder"
  | "component"
  | "hook"
  | "function"
  | "class"
  | "interface"
  | "enum"
  | "constant"
  | "route"
  | "configuration";

export interface SearchHit {
  id: string;
  kind: SearchKind;
  label: string;
  path: string;
  context: string;
}

export interface SelectionAnalysis {
  summary: string;
  purpose: string;
  filePath: string | null;
  complexity: Complexity;
  dependencies: string[];
  dependents: string[];
  linesOfCode: number;
  documentation: string | null;
  recentChanges: { at: string; text: string }[];
  riskScore: number; // 0..100
  ownership: { login: string; avatarUrl: string; contributions: number }[];
  recommendations: string[];
}
