import asyncio
from pathlib import PurePosixPath

from models.analysis import (
    RepositoryInfo,
    StructureAnalysis,
    TechStackAnalysis,
    ProjectClassification,
    HealthAnalysis,
    ActivityAnalysis,
    RepositorySummary,
)

from models.analysis import ArchitectureAnalysis
from models.architecture_blueprint import ArchitectureBlueprint
from models.dna import RepositoryDNA
from services.github_service import GitHubService
from models.response import AnalysisResponse
from services.analyzers.structure import (
    StructureAnalyzer,
    build_repository_tree,
)
from services.analyzers.tech_stack import TechStackAnalyzer
from services.analyzers.architecture import ArchitectureAnalyzer
from services.analyzers.classification import (
    ProjectClassificationAnalyzer,
)
from services.analyzers.health import HealthAnalyzer
from services.analyzers.product_identity import ProductIdentityAnalyzer
from services.analyzers.activity import ActivityAnalyzer
from services.analyzers.repository_identity import RepositoryIdentityAnalyzer
from services.intelligence_engine import IntelligenceEngine
from services.analyzers.repository_summary import (
    RepositorySummaryAnalyzer,
)
from services.analyzers.purpose import PurposeAnalyzer

from services.knowledge.builder import KnowledgeBuilder

from services.architecture_blueprint_builder import ArchitectureBlueprintBuilder
from models.evidence import RepositoryFileEvidence
from core.config import settings

class AnalysisService:
    """
    Orchestrates repository analysis.
    """
    SOURCE_MAX_TREE_ITEMS = 10_000
    SOURCE_SKIP_DIRS = {
        ".git", ".hg", ".svn", "node_modules", "vendor", "bower_components",
        "dist", "build", "coverage", ".next", ".nuxt", ".venv", "venv",
        "__pycache__", "target", "bin", "obj",
    }
    SOURCE_SKIP_NAMES = {
        ".env", ".env.local", ".env.production", ".env.development",
        "npm-shrinkwrap.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "poetry.lock", "pipfile.lock", "composer.lock",
    }
    SOURCE_EXTENSIONS = {
        ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
        ".java", ".kt", ".go", ".rs", ".rb", ".php", ".cs", ".cpp", ".c",
        ".h", ".hpp", ".swift", ".sql", ".html", ".css", ".scss", ".vue",
        ".md", ".mdx", ".rst", ".txt", ".json", ".yaml", ".yml", ".toml",
        ".ini", ".cfg", ".xml", ".gradle",
    }
    SOURCE_PRIORITY_NAMES = {
        "readme.md", "readme.rst", "pyproject.toml", "requirements.txt",
        "package.json", "go.mod", "cargo.toml", "pom.xml", "dockerfile",
    }
    """
    IMPORTANT_FILES = [

        # Frontend
        "package.json",
        "vite.config.ts",
        "vite.config.js",
        "next.config.js",
        "next.config.mjs",
        "nuxt.config.ts",
        "nuxt.config.js",
        "angular.json",
        "astro.config.mjs",
        "astro.config.ts",

        # Python
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",

        # Java
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",

        # Node
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",

        # Go
        "go.mod",

        # Rust
        "Cargo.toml",

        # PHP
        "composer.json",

        # Docker
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",

        # CI/CD
        ".github/workflows/ci.yml",
        ".github/workflows/build.yml",
        ".github/workflows/deploy.yml",

        # Cloud
        "vercel.json",
        "netlify.toml",
        "firebase.json",
        "amplify.yml",
        "serverless.yml",

        # General
        "README.md",
        "LICENSE",
    ]
    

    IMPORTANT_FILES = [
        "package.json",
        "requirements.txt",
        "pom.xml",
        "Dockerfile",
    ]
    """

    def __init__(self, config=settings):

        self.github = GitHubService()
        self.source_max_files = config.SOURCE_MAX_FILES
        self.source_max_file_bytes = config.SOURCE_MAX_FILE_BYTES
        self.source_max_total_bytes = config.SOURCE_MAX_TOTAL_BYTES
        self.source_max_concurrency = config.SOURCE_MAX_CONCURRENCY
        self.structure_analyzer = StructureAnalyzer()
        self.tech_stack_analyzer = TechStackAnalyzer()
        self.health_analyzer = HealthAnalyzer()
        self.activity_analyzer = ActivityAnalyzer()
        self.summary_analyzer = RepositorySummaryAnalyzer()
        self.architecture_analyzer = ArchitectureAnalyzer()
        self.classification_analyzer = ProjectClassificationAnalyzer()
        self.knowledge_builder = KnowledgeBuilder()
        self.purpose_analyzer = PurposeAnalyzer()
        self.product_identity_analyzer = ProductIdentityAnalyzer()
        self.repository_identity_analyzer = RepositoryIdentityAnalyzer()
        self.intelligence_engine = IntelligenceEngine()
        self.architecture_blueprint_builder = ArchitectureBlueprintBuilder()

    def select_source_paths(self, tree: list[dict]) -> tuple[list[str], list[str]]:
        """Select deterministic, bounded text evidence paths from a Git tree."""
        selected: list[tuple[int, str]] = []
        notes: list[str] = []
        considered = 0
        skipped_secret = 0
        skipped_generated = 0
        skipped_unsupported = 0
        for item in tree[: self.SOURCE_MAX_TREE_ITEMS]:
            path = item.get("path")
            if item.get("type") not in {"blob", "file"} or not isinstance(path, str):
                continue
            considered += 1
            parts = PurePosixPath(path).parts
            lower_path = path.lower()
            name = parts[-1].lower()
            if any(part.lower() in self.SOURCE_SKIP_DIRS for part in parts[:-1]):
                skipped_generated += 1
                continue
            if name in self.SOURCE_SKIP_NAMES or name.startswith(".env"):
                skipped_secret += 1
                continue
            if any(token in name for token in ("credential", "secret", "private_key")):
                skipped_secret += 1
                continue
            if item.get("size", 0) > self.source_max_file_bytes:
                notes.append(f"Skipped oversized source evidence: {path}.")
                continue
            suffix = PurePosixPath(path).suffix.lower()
            is_readme = name.startswith("readme.")
            is_documentation = lower_path.startswith(("docs/", "doc/"))
            is_priority = name in self.SOURCE_PRIORITY_NAMES
            if suffix not in self.SOURCE_EXTENSIONS and not is_readme and not is_documentation and not is_priority:
                skipped_unsupported += 1
                continue
            if (
                any(part.lower() in {"generated", "vendor"} for part in parts[:-1])
                or name.startswith("generated")
                or ".generated." in name
            ):
                skipped_generated += 1
                continue
            score = 0
            if name in self.SOURCE_PRIORITY_NAMES:
                score += 100
            if is_readme:
                score += 90
            if is_documentation:
                score += 60
            if any(part.lower() in {"tests", "test", "spec", "__tests__"} for part in parts[:-1]):
                score += 35
            if suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs"}:
                score += 25
            score -= len(parts)
            selected.append((score, path))

        selected.sort(key=lambda item: (-item[0], item[1].casefold()))
        paths = [path for _, path in selected[: self.source_max_files]]
        if considered > len(paths):
            notes.append(
                f"Source evidence bounded to {len(paths)} files from {considered} eligible tree files."
            )
        if len(tree) > self.SOURCE_MAX_TREE_ITEMS:
            notes.append(f"Repository tree truncated at {self.SOURCE_MAX_TREE_ITEMS} items for source selection.")
        if skipped_secret:
            notes.append(f"Skipped {skipped_secret} secret-like or environment files.")
        if skipped_generated:
            notes.append(f"Skipped {skipped_generated} vendored, generated, or build-output files.")
        if skipped_unsupported:
            notes.append(f"Skipped {skipped_unsupported} non-text or unsupported file types.")
        return paths, notes

    @staticmethod
    def _file_type(path: str) -> str:
        suffix = PurePosixPath(path).suffix.lower()
        if PurePosixPath(path).name.lower().startswith("readme"):
            return "documentation"
        if "test" in PurePosixPath(path).parts or "spec" in PurePosixPath(path).name.lower():
            return "test"
        if suffix in {".md", ".mdx", ".rst", ".txt"}:
            return "documentation"
        if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml"}:
            return "configuration"
        return "source"

    def _build_source_evidence(
        self,
        files: dict[str, str],
        readme: str,
    ) -> tuple[list[RepositoryFileEvidence], list[str]]:
        evidence: list[RepositoryFileEvidence] = []
        notes: list[str] = []
        total_bytes = 0
        for path in sorted(files, key=str.casefold):
            raw = files[path]
            encoded = raw.encode("utf-8", errors="ignore")
            if not encoded:
                continue
            remaining = self.source_max_total_bytes - total_bytes
            if remaining <= 0:
                notes.append("Source evidence truncated at the total byte limit.")
                break
            limit = min(self.source_max_file_bytes, remaining)
            truncated = len(encoded) > limit
            text = encoded[:limit].decode("utf-8", errors="ignore")
            line_count = max(1, text.count("\n") + 1)
            evidence.append(
                RepositoryFileEvidence(
                    path=path,
                    file_type=self._file_type(path),
                    start_line=1,
                    end_line=line_count,
                    text=text,
                    truncated=truncated,
                )
            )
            total_bytes += len(text.encode("utf-8"))
            if truncated:
                notes.append(f"Truncated source evidence: {path}.")

        if readme and not any(PurePosixPath(item.path).name.lower().startswith("readme.") for item in evidence):
            encoded = readme.encode("utf-8", errors="ignore")
            limit = min(self.source_max_file_bytes, self.source_max_total_bytes - total_bytes)
            if limit > 0:
                text = encoded[:limit].decode("utf-8", errors="ignore")
                evidence.insert(
                    0,
                    RepositoryFileEvidence(
                        path="README.md",
                        file_type="documentation",
                        end_line=max(1, text.count("\n") + 1),
                        text=text,
                        truncated=len(encoded) > limit,
                    ),
                )
                if len(encoded) > limit:
                    notes.append("Truncated source evidence: README.md.")
        return evidence, notes

    async def analyze_repository(
        self,
        owner: str,
        repo: str,
    ) -> AnalysisResponse:

        metadata = await self.github.get_repository_metadata(
            owner,
            repo,
        )

        default_branch = metadata["default_branch"]

        (
            languages,
            contributors,
            branches,
            commits,
            issues,
            pull_requests,
            pr_count,
            total_pr_count,
            releases,
            release_count,
            readme,
            tree_response,
        ) = await asyncio.gather(

            self.github.get_languages(owner, repo),
            self.github.get_contributors(owner, repo),
            self.github.get_branches(owner, repo),
            self.github.get_commits(owner, repo),

            self.github.get_issues(owner, repo),
            self.github.get_pull_requests(owner, repo),

            self.github.get_pull_request_count(owner, repo),
            self.github.get_total_pull_request_count(owner, repo),

            self.github.get_releases(owner, repo),
            self.github.get_release_count(owner, repo),
            self.github.get_readme(owner, repo),

            self.github.get_repository_tree(
                owner,
                repo,
                default_branch,
            ),
        )

        # ← AFTER the gather finishes

        open_pr_count = pr_count["total_count"]
        open_issue_count = max(metadata.get("open_issues_count", 0) - open_pr_count, 0)

        tree = tree_response.get(
            "tree",
            [],
        )

        repository_tree = build_repository_tree(tree)

        files_to_download, source_notes = self.select_source_paths(tree)
        important_files = await self.github.get_multiple_files(
            owner,
            repo,
            files_to_download,
            max_concurrency=self.source_max_concurrency,
        )
        source_evidence, evidence_notes = self._build_source_evidence(important_files, readme)

        tech_stack = self.tech_stack_analyzer.analyze(
            tree,
            important_files,
        )

        structure = self.structure_analyzer.analyze(
            tree,
            important_files,
            tech_stack,
        )

        architecture = self.architecture_analyzer.analyze(
            tree,
            important_files,
            tech_stack,
            metadata,
            readme,
        )

        classification = self.classification_analyzer.analyze(
            tree,
            tech_stack,
            metadata,
            readme,
        )

        health = self.health_analyzer.analyze(
            metadata,
            tree,
            tech_stack,
            releases,
            readme,
            important_files,
        )

        activity = self.activity_analyzer.analyze(
            metadata,
            commits,
            issues,
            pull_requests,
            releases,
            open_issue_count,
            open_pr_count,
            total_pull_request_count=total_pr_count,
            total_release_count=release_count,
        )


        repository=RepositoryInfo(
            name=metadata["name"],
            full_name=metadata["full_name"],
            owner=metadata["owner"]["login"],
            owner_avatar=metadata["owner"]["avatar_url"],
            description=metadata["description"],
            html_url=metadata["html_url"],
            default_branch=metadata["default_branch"],
            language=metadata["language"],
            topics=metadata.get("topics", []),
            stars=metadata["stargazers_count"],
            forks=metadata["forks_count"],
            watchers=metadata["watchers_count"],
            open_issues=open_issue_count,
            created_at=metadata["created_at"],
            updated_at=metadata["updated_at"],
        )

        knowledge = self.knowledge_builder.build(
            repository=repository,
            readme=readme,
            tree=repository_tree,
            architecture=architecture,
            structure=structure,
            tech_stack=tech_stack,
            health=health,
            activity=activity,
            contributors=contributors,
            branches=branches,
            releases=releases,
            issues=issues,
            pull_requests=pull_requests,
        )

        blueprint = self.architecture_blueprint_builder.build(
            knowledge
        )

        product_identity = self.product_identity_analyzer.analyze(
            knowledge,
        )

        repository_identity = self.repository_identity_analyzer.analyze(
            knowledge,
        )

        purpose = self.purpose_analyzer.analyze(
            knowledge,
            product_identity,
        )

        summary = self.summary_analyzer.analyze(
            metadata,
            readme,
            tech_stack,
            architecture,
            classification,
            structure,
            health,
            activity,
        )

        return AnalysisResponse(

            repository=repository,
            
            structure=StructureAnalysis(
                **structure,
            ),

            tech_stack=TechStackAnalysis(
                **tech_stack,
            ),

            architecture=ArchitectureAnalysis(
                **architecture,
            ),

            classification=ProjectClassification(
                **classification,
            ),

            health=HealthAnalysis(
                **health,
            ),

            activity=ActivityAnalysis(
                **activity,
            ),

            summary=RepositorySummary(
                **summary,
            ),

            purpose=purpose,
            product_identity=product_identity,
            repository_identity=repository_identity,
            knowledge=knowledge,
            blueprint=blueprint,
            source_evidence=source_evidence,
            source_evidence_notes=[*source_notes, *evidence_notes],
        )

    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
    ):
        """
        Fetch and build the repository tree.
        """
        

        metadata = await self.github.get_repository_metadata(
            owner,
            repo,
        )

        default_branch = metadata["default_branch"]

        tree_response = await self.github.get_repository_tree(
            owner,
            repo,
            default_branch,
        )

        tree = tree_response.get(
            "tree",
            [],
        )

        return build_repository_tree(tree)