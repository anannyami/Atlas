import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.analyzers.activity import ActivityAnalyzer


class ActivityAnalyzerTests(unittest.TestCase):
    def test_issue_sample_excludes_pull_request_records(self) -> None:
        result = ActivityAnalyzer().analyze(
            metadata={"stargazers_count": 10, "forks_count": 2},
            commits=[],
            issues=[
                {"number": 1, "title": "Bug report"},
                {"number": 2, "title": "Feature request"},
                {"number": 3, "title": "Pull request issue record", "pull_request": {"url": "https://api.github.com/repos/example/repo/pulls/3"}},
            ],
            pull_requests=[{"number": 3}],
            releases=[{"tag_name": "v1"}],
            open_issue_count=2,
            open_pr_count=1,
        )

        self.assertEqual(result["recent_issues"], 2)
        self.assertEqual(result["recent_pull_requests"], 1)
        self.assertEqual(result["releases"], 1)
        self.assertEqual(result["observed_samples"], 3)
        self.assertTrue(any("open issues excluding pull requests" in item for item in result["explanations"]))

    def test_open_issue_metric_is_consistent_and_commit_recency_is_available(self) -> None:
        result = ActivityAnalyzer().analyze(
            metadata={"stargazers_count": 0, "forks_count": 0},
            commits=[{"commit": {"committer": {"date": "2026-09-30T00:00:00Z"}}} for _ in range(3)],
            issues=[{"number": 1}],
            pull_requests=[{"number": 2}, {"number": 3}],
            releases=[{"tag_name": "v1"}, {"tag_name": "v2"}],
            open_issue_count=7,
            open_pr_count=2,
        )

        self.assertEqual(result["recent_commits"], 3)
        self.assertEqual(result["recent_issues"], 7)
        self.assertEqual(result["open_issues"], 7)
        self.assertEqual(result["recent_pull_requests"], 2)
        self.assertEqual(result["releases"], 2)
        self.assertIsNotNone(result["last_commit_days"])
        self.assertTrue(any("open issues excluding pull requests" in item for item in result["explanations"]))


if __name__ == "__main__":
    unittest.main()
