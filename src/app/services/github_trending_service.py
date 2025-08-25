"""
Provides a service for interacting with GitHub Trending.
"""
from typing import List, Dict

import aiohttp

from ..core.config import settings
from ..core.logging_config import get_logger

logger = get_logger(__name__)


class GitHubTrendingService:
    """A service class for handling GitHub Trending interactions."""

    def __init__(self):
        self.api_url = settings.GITHUB_TRENDING_URL
        self.timeout = settings.API_TIMEOUT
        self.headers = {
            'Accept': 'application/json'
        }

    async def get_trending_repos(self) -> List[Dict[str, str]]:
        """
        Fetches trending repositories from the OSS Insight API.

        Returns:
            A list of dictionaries containing repository information.
        """
        async with aiohttp.ClientSession() as client:
            try:
                async with client.get(
                    self.api_url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Extract repository information from JSON response
                    repos = self._extract_trending_repos(data)
                    return repos

            except aiohttp.ClientError as e:
                logger.error(
                    "Error fetching GitHub trending data",
                    error=str(e),
                    exc_info=True
                )
                raise ValueError(
                    f"Could not retrieve GitHub trending data: {str(e)}"
                ) from e
            except (ValueError, KeyError) as e:
                logger.error(
                    "Unexpected error while fetching GitHub trending data",
                    error=str(e),
                    exc_info=True
                )
                raise ValueError(
                    f"An error occurred while fetching GitHub trending data: {str(e)}"
                ) from e

    def _extract_trending_repos(self, data: dict) -> List[Dict[str, str]]:
        """
        Extract trending repository information from JSON response.
        """
        try:
            repos = []

            # Navigate through the JSON structure to get repository data
            if 'data' in data and 'rows' in data['data']:
                for row in data['data']['rows']:
                    if 'repo_name' in row:
                        repo_name = row['repo_name']
                        if repo_name and len(repo_name) < 100:  # Sanity check
                            # Extract additional information
                            description = row.get('description', '')
                            language = row.get('primary_language', '')
                            stars = row.get('stars', '0')

                            # Construct GitHub URL
                            github_url = f"https://github.com/{repo_name}"

                            repo_info = {
                                'name': repo_name,
                                'description': description,
                                'language': language,
                                'stars': stars,
                                'url': github_url
                            }
                            repos.append(repo_info)

            # If no repos found, return empty list instead of placeholder
            if not repos:
                logger.warning("No trending repositories found in API response")
                return []

            return repos[:5]  # Return top 5 repos

        except (KeyError, TypeError) as e:
            logger.warning(
                "Failed to extract trending repos from JSON",
                error=str(e)
            )
            return []
