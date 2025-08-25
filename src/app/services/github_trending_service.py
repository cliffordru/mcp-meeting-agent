"""
Provides a service for interacting with the GitHub Trending API.
"""
import aiohttp
from typing import List

from ..core.config import settings
from ..core.logging_config import get_logger

logger = get_logger(__name__)


class GitHubTrendingService:
    """A service class for handling GitHub Trending API interactions."""

    def __init__(self):
        self.api_url = settings.GITHUB_TRENDING_URL
        self.timeout = settings.API_TIMEOUT

    async def get_trending_repos(self) -> List[dict]:
        """
        Fetches trending repositories from the GitHub Trending API.

        Returns:
            A list of trending repository dictionaries.
        """
        async with aiohttp.ClientSession() as client:
            try:
                async with client.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Extract repository data from the response
                    repos = []
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            if isinstance(item, dict):
                                repo = {
                                    'name': item.get('repo_name', 'Unknown'),
                                    'description': item.get('description', 'No description available'),
                                    'language': item.get('language', 'Unknown'),
                                    'stars': item.get('stars', 0),
                                    'url': f"https://github.com/{item.get('repo_name', '')}"
                                }
                                repos.append(repo)

                    if repos:
                        logger.info(f"Successfully fetched {len(repos)} trending repos from API")
                        return repos
                    else:
                        logger.warning("No trending repositories found in API response")
                        return self._get_fallback_repos()

            except aiohttp.ClientResponseError as e:
                logger.error(
                    "Error fetching trending repos",
                    error=str(e),
                    status_code=e.status,
                    url=self.api_url
                )
                return self._get_fallback_repos()
            except aiohttp.ClientError as e:
                logger.error(
                    "Error fetching trending repos",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_repos()
            except Exception as e:
                logger.error(
                    "Unexpected error while fetching trending repos",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_repos()

    def _get_fallback_repos(self) -> List[dict]:
        """Returns fallback trending repositories when the API is unavailable."""
        logger.info("Using fallback trending repositories")
        return [
            {
                'name': 'langchain-ai/langchain',
                'description': 'Building applications with LLMs through composability',
                'language': 'Python',
                'stars': 50000,
                'url': 'https://github.com/langchain-ai/langchain'
            },
            {
                'name': 'openai/openai-python',
                'description': 'The official Python library for the OpenAI API',
                'language': 'Python',
                'stars': 15000,
                'url': 'https://github.com/openai/openai-python'
            },
            {
                'name': 'microsoft/vscode',
                'description': 'Visual Studio Code is a code editor redefined and optimized for building and debugging modern web and cloud applications',
                'language': 'TypeScript',
                'stars': 150000,
                'url': 'https://github.com/microsoft/vscode'
            }
        ]
