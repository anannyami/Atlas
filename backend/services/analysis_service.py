import asyncio

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

class AnalysisService:
    """
    Orchestrates repository analysis.
    """
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

    def __init__(self):

        self.github = GitHubService()
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
            issue_count,
            pr_count,
            releases,
            readme,
            tree_response,
        ) = await asyncio.gather(

            self.github.get_languages(owner, repo),
            self.github.get_contributors(owner, repo),
            self.github.get_branches(owner, repo),
            self.github.get_commits(owner, repo),

            self.github.get_issues(owner, repo),
            self.github.get_pull_requests(owner, repo),

            self.github.get_issue_count(owner, repo),
            self.github.get_pull_request_count(owner, repo),

            self.github.get_releases(owner, repo),
            self.github.get_readme(owner, repo),

            self.github.get_repository_tree(
                owner,
                repo,
                default_branch,
            ),
        )

        # ← AFTER the gather finishes

        open_issue_count = issue_count["total_count"]
        open_pr_count = pr_count["total_count"]

        tree = tree_response.get(
            "tree",
            [],
        )

        repository_tree = build_repository_tree(tree)

        tree_paths = {
            item["path"]
            for item in tree
        }

        candidate_files = [

        # -----------------------------
        # JavaScript / TypeScript
        # -----------------------------
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",

        "vite.config.ts",
        "vite.config.js",

        "next.config.js",
        "next.config.mjs",
        "next.config.ts",

        "nuxt.config.ts",
        "nuxt.config.js",

        "angular.json",

        "astro.config.mjs",
        "astro.config.ts",

        "svelte.config.js",

        "tsconfig.json",

        # -----------------------------
        # Python
        # -----------------------------
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "poetry.lock",

        # -----------------------------
        # Java
        # -----------------------------
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",

        # -----------------------------
        # Rust
        # -----------------------------
        "Cargo.toml",

        # -----------------------------
        # Go
        # -----------------------------
        "go.mod",

        # -----------------------------
        # PHP
        # -----------------------------
        "composer.json",

        # -----------------------------
        # .NET
        # -----------------------------
        "*.csproj",

        # -----------------------------
        # Docker
        # -----------------------------
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",

        # -----------------------------
        # Cloud
        # -----------------------------
        "vercel.json",
        "netlify.toml",
        "firebase.json",
        "amplify.yml",
        "serverless.yml",
    ]

        files_to_download = []

        SKIP_PREFIXES = (
            "test/",
            "tests/",
            "examples/",
            "example/",
            "fixtures/",
            "bench/",
            "benchmark/",
            "docs/",
            ".github/",
        )

        for repo_path in tree_paths:

            normalized = repo_path.lower()

            if normalized.startswith(SKIP_PREFIXES):
                continue

            if "/test/" in normalized:
                continue

            if "/tests/" in normalized:
                continue

            if "/example/" in normalized:
                continue

            if "/examples/" in normalized:
                continue

            if "/fixture/" in normalized:
                continue

            if "/fixtures/" in normalized:
                continue

            if "/node_modules/" in normalized:
                continue

            filename = repo_path.split("/")[-1]

            if filename in candidate_files:
                files_to_download.append(repo_path)

        files_to_download = list(dict.fromkeys(files_to_download))

        # Remove duplicates while preserving order
        files_to_download = list(dict.fromkeys(files_to_download))

        print("\n========== TECH STACK DEBUG ==========")
        print(f"Candidate files found: {len(files_to_download)}")

        print("Downloading:")
        for path in files_to_download:
            print(path)

        print("======================================\n")

        files_to_download = files_to_download[:30]
        important_files = await self.github.get_multiple_files(
            owner,
            repo,
            files_to_download,
        )

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

        print("Fetching repository tree...")

        tree_response = await self.github.get_repository_tree(
            owner,
            repo,
            default_branch,
        )

        print("Repository tree fetched successfully")

        tree = tree_response.get(
            "tree",
            [],
        )

        return build_repository_tree(tree)