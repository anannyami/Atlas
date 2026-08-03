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

    async def _request(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> httpx.Response:

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = await self.client.get(
                url,
                params=params,
            )
        except httpx.RemoteProtocolError:
            response = await self.client.get(
                url,
                params=params,
            )

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
            raise GitHubAPIError(
                response.status_code,
                response.text,
            )

        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                response.text,
            )

        return response

    async def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> Any:

        response = await self._request(
            endpoint,
            params=params,
        )

        return response.json()

    async def get_response(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> httpx.Response:

        return await self._request(
            endpoint,
            params=params,
        )

    

    async def close(self):
        """
        Close the shared AsyncClient.
        """

        await self.client.aclose()

