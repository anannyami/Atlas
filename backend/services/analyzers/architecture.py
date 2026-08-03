from __future__ import annotations

from collections import defaultdict
from typing import Any


class ArchitectureAnalyzer:
    """
    Detects the architectural organization of a repository.

    This analyzer remains heuristic and additive. It preserves the existing
    architecture fields while adding phase-four signals, confidence, and a
    human-readable summary.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        files: dict[str, str] | None = None,
        tech_stack: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        readme: str | None = None,
    ) -> dict:
        files = files or {}
        tech_stack = tech_stack or {}
        metadata = metadata or {}
        readme_text = (readme or "").lower()

        paths = {item["path"] for item in tree}
        lower_paths = {path.lower() for path in paths}

        result = {
            "style": "Standard Repository",
            "applications": [],
            "workspace": [],
            "modules": [],
            "deployment": [],
            "frontend_frameworks": [],
            "backend_frameworks": [],
            "databases": [],
            "cloud": [],
            "authentication": [],
            "api_styles": [],
            "architecture_patterns": [],
            "organization": [],
            "confidence": 0.0,
            "summary": "",
        }

        def get_file(filename: str) -> str:
            for path, content in files.items():
                if path == filename or path.endswith("/" + filename):
                    return content
            return ""

        def add(category: str, value: str):
            if value not in result[category]:
                result[category].append(value)

        def add_signal(category: str, name: str, confidence: float, evidence: list[str]):
            add(
                category,
                {
                    "name": name,
                    "confidence": round(confidence, 2),
                    "evidence": evidence,
                },
            )

        def signal_score(evidence_count: int, base: float = 0.6) -> float:
            return min(0.99, base + evidence_count * 0.08)

        package_json = get_file("package.json").lower()
        pyproject = get_file("pyproject.toml").lower()
        requirements = get_file("requirements.txt").lower()
        pom = get_file("pom.xml").lower()
        gradle = (get_file("build.gradle") + "\n" + get_file("build.gradle.kts")).lower()
        cargo = get_file("Cargo.toml").lower()
        go_mod = get_file("go.mod").lower()
        repo_text = "\n".join([package_json, pyproject, requirements, pom, gradle, cargo, go_mod, readme_text])

        def any_path(*needles: str) -> bool:
            return any(any(needle in path for needle in needles) for path in lower_paths)

        # Applications and workspace structure
        if any(path.startswith(("web/", "frontend/", "client/", "ui/")) for path in lower_paths):
            add("applications", "Web")
        if any(path.startswith(("mobile/", "android/", "ios/", "flutter/")) for path in lower_paths):
            add("applications", "Mobile")
        if any(path.startswith(("desktop/", "electron/", "tauri/")) for path in lower_paths):
            add("applications", "Desktop")
        if any(path.startswith(("cli/", "cmd/", "bin/")) for path in lower_paths):
            add("applications", "CLI")

        if "[workspace]" in cargo:
            add("workspace", "Cargo Workspace")
        if "pnpm-workspace.yaml" in lower_paths:
            add("workspace", "pnpm Workspace")
        if "package.json" in lower_paths and '"workspaces"' in package_json:
            add("workspace", "npm Workspaces")

        if any(path.startswith(("apps/", "packages/", "modules/", "services/", "shared/", "common/")) for path in lower_paths):
            add("modules", "Workspace Modules")
        if any(path.startswith("packages/") for path in lower_paths):
            add("modules", "Packages")
        if any(path.startswith("crates/") for path in lower_paths):
            add("modules", "Rust Crates")
        if any(path.startswith(("libs/", "shared/", "common/")) for path in lower_paths):
            add("modules", "Shared Libraries")

        # Deployment
        if any("dockerfile" in path for path in lower_paths):
            add("deployment", "Docker")
        if any("docker-compose" in path or "compose.yml" in path or "compose.yaml" in path for path in lower_paths):
            add("deployment", "Docker Compose")
        if any("kubernetes" in path or "k8s" in path for path in lower_paths):
            add("deployment", "Kubernetes")
        if "vercel.json" in lower_paths:
            add("deployment", "Vercel")
        if "netlify.toml" in lower_paths:
            add("deployment", "Netlify")
        if ".github/workflows" in " ".join(lower_paths):
            add("deployment", "GitHub Actions")

        # Framework / technology signals
        frontend_map = {
            "react": "React",
            "next": "Next.js",
            "vue": "Vue",
            "@angular/core": "Angular",
            "svelte": "Svelte",
            "astro": "Astro",
            "nuxt": "Nuxt",
            "vite": "Vite",
            "tailwindcss": "Tailwind CSS",
        }
        backend_map = {
            "fastapi": "FastAPI",
            "express": "Express",
            "@nestjs/core": "NestJS",
            "fastify": "Fastify",
            "spring-boot": "Spring Boot",
            "django": "Django",
            "flask": "Flask",
        }
        database_map = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "sqlite": "SQLite",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "sqlalchemy": "SQLAlchemy",
            "typeorm": "TypeORM",
            "prisma": "Prisma",
        }
        cloud_map = {
            "azure": "Azure",
            "aws": "AWS",
            "google cloud": "Google Cloud",
            "firebase": "Firebase",
            "vercel": "Vercel",
            "netlify": "Netlify",
            "supabase": "Supabase",
        }

        frontend_signals = []
        for dependency, framework in frontend_map.items():
            if dependency in repo_text:
                frontend_signals.append(framework)
        if frontend_signals:
            add_signal("frontend_frameworks", frontend_signals[0], signal_score(len(frontend_signals)), frontend_signals[:4])

        backend_signals = []
        for dependency, framework in backend_map.items():
            if dependency in repo_text:
                backend_signals.append(framework)
        if backend_signals:
            add_signal("backend_frameworks", backend_signals[0], signal_score(len(backend_signals)), backend_signals[:4])

        database_signals = []
        for dependency, database in database_map.items():
            if dependency in repo_text:
                database_signals.append(database)
        if database_signals:
            for database in database_signals[:3]:
                add_signal("databases", database, signal_score(len(database_signals), 0.58), database_signals[:4])

        cloud_signals = []
        for keyword, provider in cloud_map.items():
            if keyword in repo_text:
                cloud_signals.append(provider)
        if cloud_signals:
            for provider in cloud_signals[:3]:
                add_signal("cloud", provider, signal_score(len(cloud_signals), 0.58), cloud_signals[:4])

        # API style
        api_evidence = []
        if any(path.startswith(("api/", "backend/api/")) for path in lower_paths):
            api_evidence.append("api folder")
        if any(keyword in repo_text for keyword in ("fastapi", "openapi", "swagger", "rest", "route", "router")):
            api_evidence.append("api conventions")
        if api_evidence:
            add_signal("api_styles", "REST", signal_score(len(api_evidence), 0.7), api_evidence)
        if any(keyword in repo_text for keyword in ("graphql", "graph ql")):
            add_signal("api_styles", "GraphQL", 0.9, ["graphql keywords"])
        if any(keyword in repo_text for keyword in ("websocket", "socket.io", "sse")):
            add_signal("api_styles", "Real-time API", 0.88, ["real-time keywords"])

        # Authentication
        auth_evidence = []
        for keyword in ("auth", "authentication", "authorization", "jwt", "oauth", "session", "signin", "login"):
            if keyword in repo_text:
                auth_evidence.append(keyword)
        if auth_evidence:
            add_signal("authentication", "Authentication", signal_score(len(auth_evidence), 0.68), auth_evidence)
            if any(keyword in repo_text for keyword in ("jwt", "token")):
                add_signal("authentication", "Token-based Auth", 0.9, auth_evidence)
            if any(keyword in repo_text for keyword in ("oauth", "openid")):
                add_signal("authentication", "OAuth / OpenID", 0.9, auth_evidence)

        # Architecture patterns and organization
        layer_dirs = {
            "Presentation": ("frontend/", "client/", "web/", "ui/", "components/", "pages/", "views/"),
            "Backend": ("backend/", "api/", "server/"),
            "Service": ("services/", "service/"),
            "Persistence": ("models/", "model/", "repositories/", "database/", "db/", "entities/", "domain/"),
            "Infrastructure": ("infra/", "infrastructure/", "docker/", ".github/", "k8s/", "terraform/"),
        }
        layers_present = []
        for layer_name, prefixes in layer_dirs.items():
            if any(path.startswith(prefixes) for path in lower_paths):
                layers_present.append(layer_name)
                add("organization", layer_name)

        if layers_present:
            add_signal("architecture_patterns", "Layered Architecture", min(0.96, 0.72 + len(layers_present) * 0.05), layers_present)

        if any(path.startswith(("controllers/", "controller/", "views/")) for path in lower_paths):
            add_signal("architecture_patterns", "MVC", 0.91, ["controllers/views"])
        if any(path.startswith(("usecases/", "use-cases/", "application/", "domain/", "infrastructure/")) for path in lower_paths):
            add_signal("architecture_patterns", "Clean Architecture", 0.92, ["layered domain folders"])
        if any(keyword in repo_text for keyword in ("hexagonal", "ports", "adapters")):
            add_signal("architecture_patterns", "Hexagonal Architecture", 0.93, ["ports/adapters"])
        if any(keyword in repo_text for keyword in ("repository pattern", "repository", "repositories")):
            add_signal("architecture_patterns", "Repository Pattern", 0.84, ["repository keywords"])
        if any(keyword in repo_text for keyword in ("dependency injection", "injectable", "service collection", "provider")):
            add_signal("architecture_patterns", "Dependency Injection", 0.88, ["DI keywords"])
        if any(path.startswith(("services/", "service/")) for path in lower_paths):
            add("organization", "Service layer")
        if any(path.startswith(("models/", "model/", "domain/", "entities/")) for path in lower_paths):
            add("organization", "Model layer")
        if any(path.startswith(("controllers/", "controller/", "routes/", "handlers/")) for path in lower_paths):
            add("organization", "Controller layer")

        # Style detection
        style_scores = defaultdict(lambda: {"score": 0.0, "evidence": []})

        def raise_style(name: str, score: float, evidence: list[str]):
            current = style_scores[name]
            if score > current["score"]:
                current["score"] = score
            for item in evidence:
                if item not in current["evidence"]:
                    current["evidence"].append(item)

        if any(path.startswith(("apps/", "packages/", "modules/")) for path in lower_paths) or "workspaces" in package_json:
            raise_style("Monorepo", 0.98, ["workspace folders"])
        if any(path.startswith(("services/", "service/", "microservices/")) for path in lower_paths):
            raise_style("Microservices", 0.95, ["services folders"])
        if any(path.startswith(("lambda/", "functions/", "serverless/")) for path in lower_paths) or any(keyword in repo_text for keyword in ("serverless", "function app")):
            raise_style("Serverless", 0.94, ["serverless indicators"])
        if layers_present:
            raise_style("Layered Architecture", min(0.96, 0.7 + len(layers_present) * 0.05), layers_present)
        if any(path.startswith(("frontend/", "client/", "web/")) for path in lower_paths) and any(path.startswith(("backend/", "server/", "api/")) for path in lower_paths):
            raise_style("Client-Server", 0.95, ["frontend/backend split"])
        if not style_scores:
            raise_style("Monolith", 0.6, ["single application layout"])

        chosen_style = sorted(style_scores.items(), key=lambda item: (-item[1]["score"], item[0].lower()))[0]
        result["style"] = chosen_style[0]
        result["confidence"] = round(chosen_style[1]["score"], 2)

        if not result["organization"] and any_path("src", "app", "api", "services", "models", "controllers"):
            result["organization"] = ["Folder organization"]

        result["summary"] = " ".join(
            part
            for part in [
                f"The repository most closely matches a {result['style'].lower()}.",
                f"Detected architecture signals include {', '.join(item['name'] for item in result['architecture_patterns'][:3])}." if result["architecture_patterns"] else "",
                f"Framework signals include {', '.join(item['name'] for item in result['frontend_frameworks'][:2] + result['backend_frameworks'][:2])}." if (result["frontend_frameworks"] or result["backend_frameworks"]) else "",
            ]
            if part
        )

        for key in (
            "applications",
            "workspace",
            "modules",
            "deployment",
            "organization",
        ):
            result[key] = sorted(dict.fromkeys(result[key]), key=str.lower)

        return result
