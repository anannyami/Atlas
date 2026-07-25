export interface StructureAnalysis {
  total_files: number;
  total_directories: number;
  max_depth: number;
  major_directories: string[];
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
}

export interface ProjectClassification {
  project_type: string;
}

export interface HealthAnalysis {
  score: number;
  checks: Record<string, boolean>;
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
  health: HealthAnalysis;
  activity: ActivityAnalysis;
  classification: ProjectClassification;
}
