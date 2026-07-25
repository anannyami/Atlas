"""
Detection rules used by the Tech Stack Analyzer.

This file contains NO detection logic.

The analyzer simply imports these dictionaries and checks
whether any of the keys are present inside dependency files,
configuration files or repository paths.
"""

# ==========================================================
# Frontend
# ==========================================================

FRONTEND_RULES = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "@angular/core": "Angular",
    "svelte": "Svelte",
    "astro": "Astro",
    "nuxt": "Nuxt",
    "vite": "Vite",
    "tailwindcss": "Tailwind CSS",
    "@reduxjs/toolkit": "Redux Toolkit",
    "redux": "Redux",
    "electron": "Electron",
}

# ==========================================================
# Backend
# ==========================================================

NODE_BACKEND_RULES = {
    "express": "Express",
    "@nestjs/core": "NestJS",
    "fastify": "Fastify",
    "koa": "Koa",
    "hapi": "Hapi",
}

PYTHON_BACKEND_RULES = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
}

JAVA_BACKEND_RULES = {
    "spring-boot": "Spring Boot",
}

RUST_BACKEND_RULES = {
    "axum": "Axum",
    "rocket": "Rocket",
    "actix-web": "Actix",
    "warp": "Warp",
}

GO_BACKEND_RULES = {
    "gin-gonic/gin": "Gin",
    "labstack/echo": "Echo",
    "fiber": "Fiber",
}

# ==========================================================
# Databases
# ==========================================================

DATABASE_RULES = {
    # PostgreSQL
    "postgresql": "PostgreSQL",
    "psycopg2": "PostgreSQL",
    "tokio-postgres": "PostgreSQL",

    # MySQL
    "mysql": "MySQL",
    "mysql2": "MySQL",
    "pymysql": "MySQL",

    # SQLite
    "sqlite": "SQLite",
    "rusqlite": "SQLite",

    # MongoDB
    "mongodb": "MongoDB",
    "mongoose": "MongoDB",
    "pymongo": "MongoDB",

    # Redis
    "redis": "Redis",

    # ORMs
    "sqlalchemy": "SQLAlchemy",
    "typeorm": "TypeORM",
    "prisma": "Prisma",
    "drizzle": "Drizzle ORM",
    "diesel": "Diesel",
    "sqlx": "SQLx",
}

# ==========================================================
# Cloud
# ==========================================================

CLOUD_FILES = {
    "vercel.json": "Vercel",
    "netlify.toml": "Netlify",
    "firebase.json": "Firebase",
    "amplify.yml": "AWS Amplify",
    "serverless.yml": "Serverless",
}

CLOUD_KEYWORDS = {
    "aws-sdk": "AWS",
    "boto3": "AWS",
    "amazonaws": "AWS",

    "azure-storage": "Azure",
    "azure-core": "Azure",
    "azure-functions": "Azure",

    "google-cloud-storage": "Google Cloud",
    "google-cloud": "Google Cloud",

    "firebase": "Firebase",
    "supabase": "Supabase",
}

# ==========================================================
# CI/CD
# ==========================================================

CI_FILES = {
    ".github/workflows": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    "Jenkinsfile": "Jenkins",
    "azure-pipelines.yml": "Azure Pipelines",
    ".circleci/config.yml": "CircleCI",
}

# ==========================================================
# Containers
# ==========================================================

CONTAINER_FILES = {
    "dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "compose.yml": "Docker Compose",
    "compose.yaml": "Docker Compose",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
}

# ==========================================================
# Package Managers
# ==========================================================

PACKAGE_MANAGER_FILES = {
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",

    "Cargo.toml": "Cargo",

    "go.mod": "Go Modules",

    "pom.xml": "Maven",

    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle",
    "gradlew": "Gradle",
    "gradlew.bat": "Gradle",
}

# ==========================================================
# Mobile
# ==========================================================

MOBILE_RULES = {
    "flutter": "Flutter",
    "react-native": "React Native",
}

MOBILE_FILES = {
    "AndroidManifest.xml": "Android",
    "Info.plist": "iOS",
}

# ==========================================================
# Language Indicators
# ==========================================================

LANGUAGE_FILES = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rs": "Rust",
    ".go": "Go",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
    ".rb": "Ruby",
}