"""Tests for the GitHubTrendingService class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.services.github_trending_service import GitHubTrendingService
import aiohttp


class TestGitHubTrendingService(unittest.TestCase):
    """Test cases for GitHubTrendingService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = GitHubTrendingService()

    def test_init(self):
        """Test GitHubTrendingService initialization."""
        service = GitHubTrendingService()
        self.assertIsInstance(service, GitHubTrendingService)
        self.assertEqual(service.api_url, "https://api.ossinsight.io/v1/trends/repos/")
        self.assertEqual(service.timeout, 30)  # API_TIMEOUT from settings

    @patch('app.services.github_trending_service.aiohttp.ClientSession')
    def test_get_trending_repos_success(self, mock_session_class):
        """Test successful trending repositories retrieval."""
        async def run_test():
            # Mock response data - using the new API format
            mock_response_data = {
                "data": [
                    {
                        "repo_name": "moeru-ai/airi",
                        "description": "Self hosted AI companion",
                        "language": "Vue",
                        "stars": 801
                    },
                    {
                        "repo_name": "plait-board/drawnix",
                        "description": "Open source whiteboard tool",
                        "language": "TypeScript",
                        "stars": 530
                    },
                    {
                        "repo_name": "printz-labs/copytrading-bot-solana",
                        "description": "Copy trading bot for Solana",
                        "language": "TypeScript",
                        "stars": 154
                    }
                ]
            }
            
            # Mock response
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            
            # Mock the session context manager
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.get = Mock(return_value=mock_response)
            
            # Mock the response context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session

            result = await self.service.get_trending_repos()

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]['name'], "moeru-ai/airi")
            self.assertEqual(result[0]['description'], "Self hosted AI companion")
            self.assertEqual(result[0]['language'], "Vue")
            self.assertEqual(result[0]['stars'], 801)
            self.assertEqual(result[0]['url'], "https://github.com/moeru-ai/airi")
        
        asyncio.run(run_test())

    @patch('app.services.github_trending_service.aiohttp.ClientSession')
    def test_get_trending_repos_api_error(self, mock_session_class):
        """Test handling of API error."""
        async def run_test():
            # Mock response that raises ClientError
            mock_response = AsyncMock()
            mock_response.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("API Error"))
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            # Mock the session context manager
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.get = Mock(return_value=mock_response)
            
            mock_session_class.return_value = mock_session

            # Should return fallback repos instead of raising exception
            result = await self.service.get_trending_repos()
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)  # Fallback repos
            self.assertEqual(result[0]['name'], 'langchain-ai/langchain')
        
        asyncio.run(run_test())

    @patch('app.services.github_trending_service.aiohttp.ClientSession')
    def test_get_trending_repos_empty_response(self, mock_session_class):
        """Test handling of empty API response."""
        async def run_test():
            # Mock empty response data
            mock_response_data = {"data": []}
            
            # Mock response
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            
            # Mock the session context manager
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.get = Mock(return_value=mock_response)
            
            # Mock the response context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session

            result = await self.service.get_trending_repos()

            # Should return fallback repos when no data
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)  # Fallback repos
            self.assertEqual(result[0]['name'], 'langchain-ai/langchain')
        
        asyncio.run(run_test())

    @patch('app.services.github_trending_service.aiohttp.ClientSession')
    def test_get_trending_repos_invalid_response(self, mock_session_class):
        """Test handling of invalid API response format."""
        async def run_test():
            # Mock invalid response data
            mock_response_data = {"invalid": "structure"}
            
            # Mock response
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            
            # Mock the session context manager
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.get = Mock(return_value=mock_response)
            
            # Mock the response context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_class.return_value = mock_session

            result = await self.service.get_trending_repos()

            # Should return fallback repos when data is invalid
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)  # Fallback repos
            self.assertEqual(result[0]['name'], 'langchain-ai/langchain')
        
        asyncio.run(run_test())

    def test_get_fallback_repos(self):
        """Test fallback repositories method."""
        fallback_repos = self.service._get_fallback_repos()
        
        self.assertIsInstance(fallback_repos, list)
        self.assertEqual(len(fallback_repos), 3)
        
        # Check first repo
        self.assertEqual(fallback_repos[0]['name'], 'langchain-ai/langchain')
        self.assertEqual(fallback_repos[0]['language'], 'Python')
        self.assertEqual(fallback_repos[0]['stars'], 50000)
        self.assertEqual(fallback_repos[0]['url'], 'https://github.com/langchain-ai/langchain')


if __name__ == '__main__':
    unittest.main()
