from datetime import datetime, timezone
from typing import Any


class ActivityAnalyzer:
    """
    Analyzes repository activity based on commits,
    pull requests, issues, releases and metadata.
    """

    def analyze(
        self,
        metadata: dict[str, Any],
        commits: list[dict[str, Any]],
        issues: list[dict[str, Any]],
        pull_requests: list[dict[str, Any]],
        releases: list[dict[str, Any]],
        open_issue_count: int,
        open_pr_count: int,
    ) -> dict:

        last_commit_days = None

        community_size = "Small"
        activity_level = "Low"
        maintenance_status = "Inactive"
        repository_maturity = "Early Stage"

        if commits:

            commit_date = commits[0]["commit"]["committer"]["date"]

            commit_datetime = datetime.fromisoformat(
                commit_date.replace("Z", "+00:00")
            )

            last_commit_days = (
                datetime.now(timezone.utc) - commit_datetime
            ).days

        stars = metadata.get("stargazers_count", 0)

        if stars >= 10000:
            community_size = "Large"

        elif stars >= 1000:
            community_size = "Medium"

        else:
            community_size = "Small"

        recent_changes = (
            len(commits)
            + len(pull_requests)
            + len(issues)
        )

        if recent_changes >= 20:
            activity_level = "High"

        elif recent_changes >= 10:
            activity_level = "Moderate"

        else:
            activity_level = "Low"

        if last_commit_days is not None:

            if last_commit_days <= 30:
                maintenance_status = "Active"

            elif last_commit_days <= 180:
                maintenance_status = "Maintained"

            else:
                maintenance_status = "Stale"

        release_count = len(releases)

        if release_count >= 20:
            repository_maturity = "Mature"

        elif release_count >= 5:
            repository_maturity = "Growing"

        else:
            repository_maturity = "Early Stage"

        return {
            "stars": metadata.get("stargazers_count", 0),
            "forks": metadata.get("forks_count", 0),
            "watchers": metadata.get("subscribers_count", 0),
            "open_issues": open_issue_count,
            "recent_commits": len(commits),
            "recent_pull_requests": open_pr_count,
            "recent_issues": open_issue_count,
            "releases": len(releases),
            "last_commit_days": last_commit_days,
            "community_size": community_size,
            "activity_level": activity_level,
            "maintenance_status": maintenance_status,
            "repository_maturity": repository_maturity,
        }