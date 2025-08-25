"""
An agent responsible for fetching GitHub trending repositories.
"""
from typing import List

from ..services.github_trending_service import GitHubTrendingService


class GitHubTrendingAgent:
    """
    Wraps the GitHubTrendingService to provide a clean interface for fetching trending repositories.
    """

    def __init__(self):
        self._service = GitHubTrendingService()

    async def get_trending_repos(self) -> List[str]:
        """
        Fetches trending repositories from GitHub.

        Returns:
            A list of repository names as strings.
        """
        trending_repos = await self._service.get_trending_repos()
        return trending_repos
