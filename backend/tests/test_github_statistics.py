import sys
import unittest
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.github_service import GitHubService


class ResponseStub:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    @property
    def links(self):
        return self.response.links

    def json(self):
        return self.response.json()


class GitHubClientStub:
    def __init__(self, pages: dict[str, int]) -> None:
        self.pages = pages
        self.calls: list[tuple[str, dict]] = []

    async def get_response(self, endpoint: str, params: dict) -> ResponseStub:
        self.calls.append((endpoint, params))
        page_count = self.pages[endpoint]
        request = httpx.Request("GET", f"https://api.github.com{endpoint}")
        headers = {}
        if page_count > 1:
            headers["Link"] = (
                f'<https://api.github.com{endpoint}?per_page=1&page={page_count}>; rel="last"'
            )
        return ResponseStub(httpx.Response(200, headers=headers, json=[{"id": 1}], request=request))

class GitHubStatisticsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.service = object.__new__(GitHubService)
        self.client = GitHubClientStub({
            "/repos/o/r/pulls": 12,
            "/repos/o/r/releases": 7,
        })
        self.service.github = self.client

    async def asyncTearDown(self) -> None:
        pass

    async def test_pr_and_release_totals_use_link_last_page_without_pagination_walk(self) -> None:
        pr_count = await self.service.get_total_pull_request_count("o", "r")
        release_count = await self.service.get_release_count("o", "r")

        self.assertEqual(pr_count, 12)
        self.assertEqual(release_count, 7)
        self.assertEqual(len(self.client.calls), 2)
        self.assertTrue(all(params == {"state": "all", "per_page": 1} or params == {"per_page": 1} for _, params in self.client.calls))

    def test_missing_last_link_falls_back_to_returned_page_length(self) -> None:
        response = httpx.Response(
            200,
            json=[{"id": 1}, {"id": 2}],
            request=httpx.Request("GET", "https://api.github.com/repos/o/r/releases"),
        )
        self.assertEqual(self.service._total_count_from_response(response), 2)


if __name__ == "__main__":
    unittest.main()
