"""
Tests for the GitHub Trending Service.
"""
import pytest
from unittest.mock import patch, AsyncMock

from app.services.github_trending_service import GitHubTrendingService


class TestGitHubTrendingService:
    """Test cases for GitHubTrendingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = GitHubTrendingService()

    def test_init(self):
        """Test service initialization."""
        assert self.service.api_url is not None
        assert self.service.timeout is not None

    @patch('app.services.BaseService._make_request')
    async def test_get_trending_repos_success(self, mock_make_request):
        """Test successful trending repos fetch."""
        # Mock successful API response
        mock_response = {
            'data': [
                {
                    'repo_name': 'test/repo1',
                    'description': 'Test repository 1',
                    'language': 'Python',
                    'stars': 1000
                },
                {
                    'repo_name': 'test/repo2',
                    'description': 'Test repository 2',
                    'language': 'JavaScript',
                    'stars': 500
                }
            ]
        }
        mock_make_request.return_value = mock_response

        repos = await self.service.get_trending_repos()

        assert len(repos) == 2
        assert repos[0]['name'] == 'test/repo1'
        assert repos[0]['description'] == 'Test repository 1'
        assert repos[0]['language'] == 'Python'
        assert repos[0]['stars'] == 1000
        assert repos[0]['url'] == 'https://github.com/test/repo1'

    @patch('app.services.BaseService._make_request')
    async def test_get_trending_repos_empty_response(self, mock_make_request):
        """Test handling of empty API response."""
        mock_make_request.return_value = {'data': []}

        repos = await self.service.get_trending_repos()

        # Should return fallback data when no repos found
        assert len(repos) > 0
        assert all('name' in repo for repo in repos)

    @patch('app.services.BaseService._make_request')
    async def test_get_trending_repos_invalid_response(self, mock_make_request):
        """Test handling of invalid API response."""
        mock_make_request.return_value = {'invalid': 'data'}

        repos = await self.service.get_trending_repos()

        # Should return fallback data when response is invalid
        assert len(repos) > 0
        assert all('name' in repo for repo in repos)

    @patch('app.services.aiohttp.ClientSession')
    async def test_get_trending_repos_api_error(self, mock_session_class):
        """Test handling of API errors."""
        # Mock aiohttp to raise an exception
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = AsyncMock(side_effect=Exception("API Error"))
        mock_session_class.return_value = mock_session

        repos = await self.service.get_trending_repos()

        # Should return fallback data when API fails
        assert len(repos) > 0
        assert all('name' in repo for repo in repos)

    def test_get_fallback_data(self):
        """Test fallback repositories method."""
        fallback_repos = self.service._get_fallback_data()
        
        assert len(fallback_repos) == 3
        assert all('name' in repo for repo in fallback_repos)
        assert all('description' in repo for repo in fallback_repos)
        assert all('language' in repo for repo in fallback_repos)
        assert all('stars' in repo for repo in fallback_repos)
        assert all('url' in repo for repo in fallback_repos)
        
        # Check specific fallback repos
        repo_names = [repo['name'] for repo in fallback_repos]
        assert 'langchain-ai/langchain' in repo_names
        assert 'openai/openai-python' in repo_names
        assert 'microsoft/vscode' in repo_names
