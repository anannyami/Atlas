import traceback

from fastapi import APIRouter, HTTPException
from typing import List
from fastapi import APIRouter
from core.github_client import GitHubClient
from models.analysis import RepositoryTreeNode

from models.request import AnalyzeRepositoryRequest
from models.response import AnalyzeRepositoryResponse

from services.analysis_service import AnalysisService

from services.repo_parser import (
    parse_repo_url,
    InvalidRepositoryURL,
)

router = APIRouter()

analysis_service = AnalysisService()

@router.get("/github-rate-limit")
async def github_rate_limit():
    client = GitHubClient()
    return await client.get("/rate_limit")


@router.post(
    "/analyze",
    response_model=AnalyzeRepositoryResponse,
)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
):
    """
    Analyze a GitHub repository.

    Workflow:
    1. Parse GitHub URL
    2. Fetch repository data
    3. Run repository analyzers
    4. Return structured analysis
    """

    try:

        owner, repo = parse_repo_url(
            str(request.repo_url)
        )

        analysis = await analysis_service.analyze_repository(
            owner,
            repo,
        )

        return AnalyzeRepositoryResponse(
            success=True,
            data=analysis,
        )

    except InvalidRepositoryURL as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc!r}",
        )

@router.get(
    "/analyze/tree",
    response_model=List[RepositoryTreeNode],
)
async def get_repository_tree(
    repo_url: str,
):
    """
    Return the repository as a nested directory tree.
    """

    try:

        owner, repo = parse_repo_url(repo_url)

        tree = await analysis_service.get_repository_tree(
            owner,
            repo,
        )

        return tree

    except InvalidRepositoryURL as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc!r}",
        )