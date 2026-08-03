from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.github_client import GitHubClient

from api.analyze import router as analyze_router

from services.repo_parser import parse_repo_url

from services.github_service import GitHubService



# Create FastAPI app FIRST
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
)


def _parse_allowed_origins(raw_value: str) -> list[str]:
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    # Keep local development working even when Vite falls back to 8081.
    local_fallbacks = {
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    }

    if any(origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in origins):
        origins.extend(sorted(local_fallbacks))

    return list(dict.fromkeys(origins))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(settings.ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)

# Create GitHub client
"""github = GitHubClient()"""
github = GitHubService()


@app.get("/")
async def root():
    return {"message": "Atlas Backend is running 🚀"}

@app.get("/test")
async def test():
    return await github.get_repository_metadata(
        "fastapi",
        "fastapi",
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}

"""
@app.get("/test")
async def test():
    repo = await github.get("/repos/facebook/react")
    return repo


@app.get("/parse")
async def parse():

    owner, repo = parse_repo_url(
        "https://github.com/facebook/react"
    )

    return {
        "owner": owner,
        "repository": repo,
    }
"""