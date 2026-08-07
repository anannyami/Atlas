from datetime import datetime, timezone
from typing import Any


class ActivityAnalyzer:
    """
    Analyzes repository activity based on commits, pull requests, issues,
    releases and metadata.
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
        explanations: list[str] = []

        if commits:
            commit_date = commits[0]["commit"]["committer"]["date"]
            commit_datetime = datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
            last_commit_days = (datetime.now(timezone.utc) - commit_datetime).days

        stars = metadata.get("stargazers_count", 0)
        if stars >= 10000:
            community_size = "Large"
        elif stars >= 1000:
            community_size = "Medium"
        else:
            community_size = "Small"

        recent_changes = len(commits) + len(pull_requests) + len(issues)
        release_count = len(releases)
        observed_samples = len(commits) + len(issues) + len(pull_requests)

        activity_score = 0
        if last_commit_days is not None:
            if last_commit_days <= 30:
                activity_score += 3
                maintenance_status = "Active"
            elif last_commit_days <= 180:
                activity_score += 2
                maintenance_status = "Maintained"
            else:
                activity_score += 1
                maintenance_status = "Stale"
        else:
            maintenance_status = "Unknown"

        if recent_changes >= 6:
            activity_score += 2
        elif recent_changes >= 3:
            activity_score += 1
        if release_count >= 5:
            activity_score += 1
        if open_issue_count > 0:
            activity_score += 1
        if open_pr_count > 0:
            activity_score += 1

        if activity_score >= 6:
            activity_level = "High"
        elif activity_score >= 3:
            activity_level = "Moderate"
        else:
            activity_level = "Low"

        if release_count >= 20:
            repository_maturity = "Mature"
        elif release_count >= 5:
            repository_maturity = "Growing"
        else:
            repository_maturity = "Early Stage"

        commit_frequency = self._frequency_label(len(commits), last_commit_days)
        issue_frequency = self._frequency_label(len(issues), last_commit_days, open_issue_count)
        pr_frequency = self._frequency_label(len(pull_requests), last_commit_days, open_pr_count)

        staleness = self._staleness_label(last_commit_days)

        explanations.append(
            f"The analyzer observed {len(commits)} commits, {len(issues)} issues, and {len(pull_requests)} pull requests from the fetched sample window."
        )
        if last_commit_days is None:
            explanations.append("No recent commit history was available to measure maintenance cadence.")
        else:
            explanations.append(f"The latest commit appears to be {last_commit_days} day(s) old.")
        explanations.append(
            "These counts reflect fetched samples and recent API windows, not repository-wide totals unless the source API provides them directly."
        )
        explanations.append(f"Release history contains {release_count} release(s), which informs maturity scoring.")

        return {
            "stars": metadata.get("stargazers_count", 0),
            "forks": metadata.get("forks_count", 0),
            "watchers": metadata.get("subscribers_count", 0),
            "open_issues": open_issue_count,
            "recent_commits": len(commits),
            "recent_pull_requests": len(pull_requests),
            "recent_issues": len(issues),
            "observed_samples": observed_samples,
            "total_samples": observed_samples,
            "open_pull_requests": open_pr_count,
            "releases": len(releases),
            "last_commit_days": last_commit_days,
            "community_size": community_size,
            "activity_level": activity_level,
            "maintenance_status": maintenance_status,
            "repository_maturity": repository_maturity,
            "commit_frequency": commit_frequency,
            "issue_frequency": issue_frequency,
            "pr_frequency": pr_frequency,
            "staleness": staleness,
            "explanations": explanations,
        }

    def _frequency_label(self, count: int, last_commit_days: int | None, open_count: int | None = None) -> str:
        if count >= 10:
            return "High"
        if count >= 4:
            return "Moderate"
        if last_commit_days is not None and last_commit_days <= 30 and (open_count or 0) > 0:
            return "Moderate"
        return "Low"

    def _staleness_label(self, last_commit_days: int | None) -> str:
        if last_commit_days is None:
            return "Unknown"
        if last_commit_days <= 14:
            return "Fresh"
        if last_commit_days <= 60:
            return "Current"
        if last_commit_days <= 180:
            return "Aging"
        return "Stale"
