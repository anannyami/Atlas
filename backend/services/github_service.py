import asyncio
import base64
from urllib.parse import parse_qs, urlparse

from core.github_client import GitHubClient


class GitHubService:
    """
    Handles all communication with the GitHub REST API.

    This service should ONLY fetch data from GitHub.
    No repository analysis should happen here.
    """

    def __init__(self):
        self.github = GitHubClient()

    # ---------------------------------------------------------
    # Repository Metadata
    # ---------------------------------------------------------

    async def get_repository_metadata(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}"
        )
    

    # ---------------------------------------------------------
    # Languages
    # ---------------------------------------------------------

    async def get_languages(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/languages"
        )

    # ---------------------------------------------------------
    # Contributors
    # ---------------------------------------------------------

    async def get_contributors(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/contributors",
            params={
                "per_page": 10,
            },
        )

    # ---------------------------------------------------------
    # Branches
    # ---------------------------------------------------------

    async def get_branches(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/branches",
            params={
                "per_page": 10,
            },
        )

    # ---------------------------------------------------------
    # Commits
    # ---------------------------------------------------------

    async def get_commits(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/commits",
            params={
                "per_page": 10,
            },
        )

    # ---------------------------------------------------------
    # Issues
    # ---------------------------------------------------------

    async def get_issues(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/issues",
            params={
                "state": "all",
                "per_page": 10,
            },
        )


    # ---------------------------------------------------------
    # Issues
    # ---------------------------------------------------------
    """
    async def get_issue_count(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            "/search/issues",
            params={
                "q": f"repo:{owner}/{repo} is:issue is:open"
            },
        )
    """

    async def get_issue_count(
        self,
        owner: str,
        repo: str,
    ):
        repository = await self.github.get(
            f"/repos/{owner}/{repo}"
        )

        return {
            "total_count": repository.get("open_issues_count", 0),
        }
    
    async def get_pull_request_count(
        self,
        owner: str,
        repo: str,
    ):
        response = await self.github.get_response(
            f"/repos/{owner}/{repo}/pulls",
            params={
                "state": "open",
                "per_page": 1,
            },
        )

        last_link = response.links.get("last")

        if last_link and last_link.get("url"):
            parsed = urlparse(last_link["url"])
            page_values = parse_qs(parsed.query).get("page", [])

            if page_values:
                try:
                    return {
                        "total_count": int(page_values[0]),
                    }
                except ValueError:
                    pass

        return {
            "total_count": len(response.json()),
        }

    
    # ---------------------------------------------------------
    # Pull Requests
    # ---------------------------------------------------------

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/pulls",
            params={
                "state": "all",
                "per_page": 10,
            },
        )

    
    # ---------------------------------------------------------
    # Releases
    # ---------------------------------------------------------

    async def get_releases(
        self,
        owner: str,
        repo: str,
    ):
        return await self.github.get(
            f"/repos/{owner}/{repo}/releases",
            params={
                "per_page": 10,
            },
        )

    # ---------------------------------------------------------
    # README
    # ---------------------------------------------------------

    async def get_readme(
        self,
        owner: str,
        repo: str,
    ) -> str:

        response = await self.github.get(
            f"/repos/{owner}/{repo}/readme"
        )

        content = ""

        if isinstance(response, dict):
            content = response.get("content", "")

            if response.get("encoding") == "base64":
                try:
                    content = base64.b64decode(content).decode(
                        "utf-8",
                        errors="ignore",
                    )
                except Exception as e:
                    content = ""

        return content

    # ---------------------------------------------------------
    # Repository Tree
    # ---------------------------------------------------------

    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ):
        """
        Fetch the complete repository tree recursively.
        Returns the full GitHub Trees API response.
        """

        response = await self.github.get(
            f"/repos/{owner}/{repo}/git/trees/{branch}",
            params={
                "recursive": 1,
            },
        )

    

        return response

    # ---------------------------------------------------------
    # File Contents
    # ---------------------------------------------------------

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> str | None:
        """
        Fetches and decodes a repository file.

        Returns None if the file does not exist.
        """

        try:

            data = await self.github.get(
                f"/repos/{owner}/{repo}/contents/{path}"
            )

            if data.get("encoding") != "base64":
                return None

            content = base64.b64decode(
                data["content"]
            ).decode(
                "utf-8",
                errors="ignore",
            )

            return content

        except Exception:
            return None

    # ---------------------------------------------------------
    # Multiple Files
    # ---------------------------------------------------------

    async def get_multiple_files(
        self,
        owner: str,
        repo: str,
        paths: list[str],
    ) -> dict[str, str]:
        """
        Downloads multiple repository files while
        limiting concurrency to avoid connection bursts.
        """

        semaphore = asyncio.Semaphore(5)

        async def fetch_file(path: str):

            async with semaphore:

                content = await self.get_file_content(
                    owner,
                    repo,
                    path,
                )

                return path, content

        tasks = [
            fetch_file(path)
            for path in paths
        ]

        results = await asyncio.gather(*tasks)

        files = {}

        for path, content in results:

            if content is not None:

                files[path] = content

        return files

    # ---------------------------------------------------------
    # Legacy Method
    # ---------------------------------------------------------

    async def analyze_repository(
        self,
        owner: str,
        repo: str,
    ):
        raise NotImplementedError(
            "Use AnalysisService.analyze_repository() instead."
        )
    """
    async def analyze_repository(
        self,
        owner: str,
        repo: str,
    ):
        """
    """
        Legacy method.

        This will be removed once AnalysisService
        becomes the main orchestration layer.
        """
    """

        (
            metadata,
            languages,
            contributors,
            branches,
            commits,
            issues,
            pull_requests,
            issue_search,
            pr_search,
            releases,
            readme,
            tree_response,
        ) = await asyncio.gather(
            self.get_repository_metadata(owner, repo),
            self.get_languages(owner, repo),
            self.get_contributors(owner, repo),
            self.get_branches(owner, repo),
            self.get_commits(owner, repo),
            self.get_issues(owner, repo),
            self.get_pull_requests(owner, repo),
            self.get_releases(owner, repo),
            self.get_readme(owner, repo),
        )

        return {
            "metadata": metadata,
            "languages": languages,
            "contributors": contributors,
            "branches": branches,
            "commits": commits,
            "issues": issues,
            "pull_requests": pull_requests,
            "releases": releases,
            "readme": readme,
        }
        """