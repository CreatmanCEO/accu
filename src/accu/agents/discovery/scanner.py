"""GitHub repository scanner for Discovery Agent."""

from datetime import datetime, timedelta

import httpx

from accu.agents.discovery.models import RepositoryMetrics


class GitHubScanner:
    """Scans GitHub for repositories matching discovery criteria."""

    SEARCH_QUERIES = {
        "abandoned_stars": "stars:{min_stars}..{max_stars} pushed:<{abandoned_date} archived:false",
        "unfinished_ideas": "stars:5..50 (topic:mvp OR topic:prototype OR topic:proof-of-concept)",
        "solo_developer": "stars:20..200 pushed:<{abandoned_date} archived:false",
        "language_specific": "language:{language} stars:{min_stars}..{max_stars} pushed:<{abandoned_date}",
    }

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    async def search(
        self,
        strategy: str,
        languages: list[str],
        min_stars: int = 5,
        max_stars: int = 500,
        max_results: int = 100,
    ) -> list[dict]:
        """Search for repositories using a specific strategy.

        Args:
            strategy: Search strategy name
            languages: List of programming languages to include
            min_stars: Minimum star count
            max_stars: Maximum star count
            max_results: Maximum number of results

        Returns:
            List of repository data dictionaries
        """
        # Calculate abandoned date (1 year ago)
        abandoned_date = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")

        query_template = self.SEARCH_QUERIES.get(strategy, self.SEARCH_QUERIES["abandoned_stars"])

        results = []

        for language in languages:
            query = query_template.format(
                min_stars=min_stars,
                max_stars=max_stars,
                abandoned_date=abandoned_date,
                language=language,
            )

            # Add language filter if not already in query
            if "language:" not in query:
                query = f"language:{language} {query}"

            repos = await self._search_repos(query, max_results - len(results))
            results.extend(repos)

            if len(results) >= max_results:
                break

        return results[:max_results]

    async def _search_repos(self, query: str, max_results: int) -> list[dict]:
        """Execute a GitHub search query."""
        repos = []
        page = 1
        per_page = min(100, max_results)

        while len(repos) < max_results:
            response = await self.client.get(
                "/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "page": page,
                    "per_page": per_page,
                },
            )

            if response.status_code == 403:
                # Rate limited
                break

            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                break

            repos.extend(items)
            page += 1

            if len(items) < per_page:
                break

        return repos[:max_results]

    async def get_metrics(self, repo: dict) -> RepositoryMetrics:
        """Get detailed metrics for a repository."""
        owner = repo["owner"]["login"]
        name = repo["name"]

        # Get contributor count
        contributors_count = await self._get_contributors_count(owner, name)

        # Get commit count for last year
        commit_count = await self._get_recent_commit_count(owner, name)

        # Calculate days since last commit
        pushed_at = repo.get("pushed_at")
        days_since_commit = 0
        if pushed_at:
            pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_since_commit = (datetime.now(pushed_date.tzinfo) - pushed_date).days

        # Get latest release info
        days_since_release = await self._get_days_since_release(owner, name)

        return RepositoryMetrics(
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
            open_issues=repo.get("open_issues_count", 0),
            watchers=repo.get("watchers_count", 0),
            contributors_count=contributors_count,
            commit_count_last_year=commit_count,
            days_since_last_commit=days_since_commit,
            days_since_last_release=days_since_release,
        )

    async def _get_contributors_count(self, owner: str, name: str) -> int:
        """Get number of contributors."""
        try:
            response = await self.client.get(
                f"/repos/{owner}/{name}/contributors",
                params={"per_page": 1, "anon": "false"},
            )
            if response.status_code == 200:
                # Get count from Link header
                link = response.headers.get("Link", "")
                if 'rel="last"' in link:
                    # Extract page number from last link
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link)
                    if match:
                        return int(match.group(1))
                return len(response.json())
        except Exception:
            pass
        return 0

    async def _get_recent_commit_count(self, owner: str, name: str) -> int:
        """Get commit count for the last year."""
        try:
            since = (datetime.utcnow() - timedelta(days=365)).isoformat() + "Z"
            response = await self.client.get(
                f"/repos/{owner}/{name}/commits",
                params={"since": since, "per_page": 1},
            )
            if response.status_code == 200:
                link = response.headers.get("Link", "")
                if 'rel="last"' in link:
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link)
                    if match:
                        return int(match.group(1))
                return len(response.json())
        except Exception:
            pass
        return 0

    async def _get_days_since_release(self, owner: str, name: str) -> int | None:
        """Get days since the last release."""
        try:
            response = await self.client.get(
                f"/repos/{owner}/{name}/releases/latest"
            )
            if response.status_code == 200:
                data = response.json()
                published_at = data.get("published_at")
                if published_at:
                    published_date = datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    )
                    return (datetime.now(published_date.tzinfo) - published_date).days
        except Exception:
            pass
        return None

    async def get_readme(self, owner: str, name: str) -> str | None:
        """Get repository README content."""
        try:
            response = await self.client.get(
                f"/repos/{owner}/{name}/readme",
                headers={"Accept": "application/vnd.github.raw+json"},
            )
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return None

    async def get_file_tree(self, owner: str, name: str, path: str = "") -> list[dict]:
        """Get repository file tree."""
        try:
            response = await self.client.get(
                f"/repos/{owner}/{name}/contents/{path}"
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return []

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
