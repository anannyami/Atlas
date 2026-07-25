from urllib.parse import urlparse


class InvalidRepositoryURL(Exception):
    """Raised when a GitHub repository URL is invalid."""
    pass


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Extract owner and repository name from a GitHub URL.
    """

    if not repo_url.startswith(("http://", "https://")):
        repo_url = f"https://{repo_url}"

    parsed = urlparse(repo_url)

    if parsed.netloc not in (
        "github.com",
        "www.github.com",
    ):
        raise InvalidRepositoryURL(
            "Only GitHub repository URLs are supported."
        )

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise InvalidRepositoryURL(
            "Repository URL must contain both owner and repository."
        )

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    return owner, repo