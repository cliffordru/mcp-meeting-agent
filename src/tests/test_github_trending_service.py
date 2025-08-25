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
        self.assertEqual(service.headers, {'Accept': 'application/json'})

    @patch('app.services.github_trending_service.aiohttp.ClientSession')
    def test_get_trending_repos_success(self, mock_session_class):
        """Test successful trending repositories retrieval."""
        async def run_test():
            # Mock response data
            mock_response_data = {
                "type": "sql_endpoint",
                "data": {
                    "columns": [],
                    "rows": [
                        {
                            "repo_name": "moeru-ai/airi",
                            "description": "Self hosted AI companion",
                            "primary_language": "Vue",
                            "stars": "801"
                        },
                        {
                            "repo_name": "plait-board/drawnix",
                            "description": "Open source whiteboard tool",
                            "primary_language": "TypeScript",
                            "stars": "530"
                        },
                        {
                            "repo_name": "printz-labs/copytrading-bot-solana",
                            "description": "Copy trading bot for Solana",
                            "primary_language": "TypeScript",
                            "stars": "154"
                        }
                    ]
                }
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
            self.assertEqual(result[0]['stars'], "801")
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

            with self.assertRaises(ValueError):
                await self.service.get_trending_repos()
        
        asyncio.run(run_test())

    def test_extract_trending_repos_with_valid_data(self):
        """Test extracting trending repos from valid JSON data."""
        data = {
            "type": "sql_endpoint",
            "data": {
                "rows": [
                    {
                        "repo_name": "test/repo1",
                        "description": "Test description 1",
                        "primary_language": "Python",
                        "stars": "100"
                    },
                    {
                        "repo_name": "test/repo2",
                        "description": "Test description 2",
                        "primary_language": "JavaScript",
                        "stars": "50"
                    }
                ]
            }
        }
        
        repos = self.service._extract_trending_repos(data)
        self.assertIsInstance(repos, list)
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]['name'], "test/repo1")
        self.assertEqual(repos[0]['description'], "Test description 1")
        self.assertEqual(repos[0]['url'], "https://github.com/test/repo1")

    def test_extract_trending_repos_with_empty_data(self):
        """Test extracting trending repos from empty data."""
        data = {"type": "sql_endpoint", "data": {"rows": []}}
        
        repos = self.service._extract_trending_repos(data)
        self.assertIsInstance(repos, list)
        self.assertEqual(len(repos), 0)

    def test_extract_trending_repos_with_invalid_data(self):
        """Test extracting trending repos from invalid data."""
        data = {"invalid": "structure"}
        
        repos = self.service._extract_trending_repos(data)
        self.assertIsInstance(repos, list)
        self.assertEqual(len(repos), 0)

    def test_extract_trending_repos_limits_to_five(self):
        """Test that extract_trending_repos limits results to 5 repos."""
        data = {
            "type": "sql_endpoint",
            "data": {
                "rows": [
                    {
                        "repo_name": f"test/repo{i}",
                        "description": f"Description {i}",
                        "primary_language": "Python",
                        "stars": str(i * 10)
                    } for i in range(10)
                ]
            }
        }
        
        repos = self.service._extract_trending_repos(data)
        self.assertIsInstance(repos, list)
        self.assertEqual(len(repos), 5)
        self.assertEqual(repos[0]['name'], "test/repo0")
        self.assertEqual(repos[4]['name'], "test/repo4")


if __name__ == '__main__':
    unittest.main()
