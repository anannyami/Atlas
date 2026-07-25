from typing import Any
from datetime import datetime, timezone
import httpx

from core.config import settings


class GitHubAPIError(Exception):
    """Raised when GitHub API returns an error."""

    def __init__(
        self,
        status_code: int,
        message: str,
    ):
        self.status_code = status_code
        self.message = message

        super().__init__(message)


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        self.timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=10.0,
            pool=30.0,
        )

        #
        # Create ONE reusable client
        #

        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
            http2=False,
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
            ),
        )

    async def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> Any:

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = await self.client.get(
                url,
                params=params,
            )
        except httpx.RemoteProtocolError:
            # Retry once if GitHub closes the connection mid-stream.
            response = await self.client.get(
                url,
                params=params,
            )

        print("===== GITHUB RATE LIMIT =====")
        print("Remaining:", response.headers.get("X-RateLimit-Remaining"))
        print("Limit:", response.headers.get("X-RateLimit-Limit"))
        print("Reset:", response.headers.get("X-RateLimit-Reset"))
        print("=============================")

        if response.status_code == 404:
            raise GitHubAPIError(
                404,
                "Repository or resource not found.",
            )

        if response.status_code == 401:
            raise GitHubAPIError(
                401,
                "Invalid GitHub token.",
            )

        if response.status_code == 403:
            print("\n========== GITHUB 403 DEBUG ==========")
            print("URL:", url)
            print("Status:", response.status_code)
            print("Remaining:", response.headers.get("X-RateLimit-Remaining"))
            print("Limit:", response.headers.get("X-RateLimit-Limit"))
            print("Response Body:")
            print(response.text)
            print("======================================\n")

            raise GitHubAPIError(
                response.status_code,
                response.text,
            )

        """

        if response.status_code == 403:

            remaining = response.headers.get(
                "X-RateLimit-Remaining",
                "",
            )

            if remaining == "0":

                raise GitHubAPIError(
                    429,
                    "GitHub rate limit exceeded.",
                )

            raise GitHubAPIError(
                403,
                "Access forbidden.",
            )
        """

        if response.status_code >= 400:

            raise GitHubAPIError(
                response.status_code,
                response.text,
            )

        return response.json()

    

    async def close(self):
        """
        Close the shared AsyncClient.
        """

        await self.client.aclose()

print("GitHub token loaded:", bool(settings.GITHUB_TOKEN))
