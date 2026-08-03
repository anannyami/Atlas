export interface StructureAnalysis {
  total_files: number;
  total_directories: number;
  max_depth: number;
  major_directories: string[];
  largest_directories: DirectoryInsight[];
  deepest_paths: DirectoryInsight[];
  major_modules: string[];
  entry_points: string[];
  important_folders: string[];
  configuration_files: string[];
  root_technologies: string[];
  summary: string;
}

export interface DirectoryInsight {
  path: string;
  file_count: number;
  depth: number;
}

export interface DetectedSignal {
  name: string;
  confidence: number;
  evidence: string[];
}

export interface TechStackAnalysis {
  languages: string[];

  frontend: string[];
  backend: string[];

  database: string[];

  cloud: string[];

  ci_cd: string[];

  package_managers: string[];

  mobile: string[];

  containers: string[];
}

export interface ArchitectureAnalysis {
  style: string;

  applications: string[];

  workspace: string[];

  modules: string[];

  deployment: string[];
  frontend_frameworks: DetectedSignal[];
  backend_frameworks: DetectedSignal[];
  databases: DetectedSignal[];
  cloud: DetectedSignal[];
  authentication: DetectedSignal[];
  api_styles: DetectedSignal[];
  architecture_patterns: DetectedSignal[];
  organization: string[];
  confidence: number;
  summary: string;
}

export interface RepositorySummary {
  overview: string;
  purpose: string;
  current_status: string;
  highlights: string[];
  source_factors: string[];
}

export interface RepositoryTree {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: RepositoryTree[];
}

export interface ProjectClassification {
  project_type: string;
  primary_classification: string;
  secondary_classifications: DetectedSignal[];
  confidence: number;
}

export interface HealthAnalysis {
  score: number;
  health?: string;
  overall_status?: string;
  checks: Record<string, boolean>;
  component_scores: Record<string, number>;
  missing_recommendations: string[];
}

export interface ActivityAnalysis {
  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;

  recent_commits: number;
  recent_pull_requests: number;
  recent_issues: number;

  releases: number;
  last_commit_days: number | null;

  community_size: string;
  activity_level: string;
  maintenance_status: string;
  repository_maturity: string;
  commit_frequency: string;
  issue_frequency: string;
  pr_frequency: string;
  staleness: string;
  explanations: string[];
}

export interface RepositoryIdentity {
  product_name: string;
  category: string;
  subtype: string;
  tagline: string;
  description: string;
  audience: string;
  capabilities: string[];
  confidence: number;
  evidence: string[];
}

export interface ProductIdentity {
  category: string;
  subcategory: string;
  title: string;
  summary: string;
  confidence: number;
  evidence: string[];
}

export interface RepositoryInfo {
  name: string;
  full_name: string;
  owner: string;
  owner_avatar: string;
  description: string | null;

  html_url: string;

  default_branch: string;
  language: string | null;
  topics: string[];

  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;

  created_at: string;
  updated_at: string;
}

export interface AnalysisResponse {
  repository: RepositoryInfo;
  structure: StructureAnalysis;
  tech_stack: TechStackAnalysis;
  architecture: ArchitectureAnalysis;
  summary: RepositorySummary;
  health: HealthAnalysis;
  activity: ActivityAnalysis;
  classification: ProjectClassification;
  product_identity?: ProductIdentity;
  repository_identity?: RepositoryIdentity;
}
