"""Tests for the GitHubTrendingAgent class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.agents.github_trending_agent import GitHubTrendingAgent


class TestGitHubTrendingAgent(unittest.TestCase):
    """Test cases for GitHubTrendingAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = GitHubTrendingAgent()

    def test_init(self):
        """Test GitHubTrendingAgent initialization."""
        agent = GitHubTrendingAgent()
        self.assertIsInstance(agent, GitHubTrendingAgent)
        self.assertIsNotNone(agent._service)

    @patch('app.services.github_trending_service.GitHubTrendingService.get_trending_repos')
    def test_get_trending_repos_success(self, mock_get_trending_repos):
        """Test successful trending repositories retrieval."""
        async def run_test():
            # Mock the service response with new format
            mock_repos = [
                {
                    'name': 'moeru-ai/airi',
                    'description': 'Self hosted AI companion',
                    'language': 'Vue',
                    'stars': '801',
                    'url': 'https://github.com/moeru-ai/airi'
                },
                {
                    'name': 'plait-board/drawnix',
                    'description': 'Open source whiteboard tool',
                    'language': 'TypeScript',
                    'stars': '530',
                    'url': 'https://github.com/plait-board/drawnix'
                },
                {
                    'name': 'printz-labs/copytrading-bot-solana',
                    'description': 'Copy trading bot for Solana',
                    'language': 'TypeScript',
                    'stars': '154',
                    'url': 'https://github.com/printz-labs/copytrading-bot-solana'
                }
            ]
            mock_get_trending_repos.return_value = mock_repos

            result = await self.agent.get_trending_repos()

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]['name'], "moeru-ai/airi")
            self.assertEqual(result[0]['description'], "Self hosted AI companion")
            self.assertEqual(result[0]['url'], "https://github.com/moeru-ai/airi")
        
        asyncio.run(run_test())

    @patch('app.services.github_trending_service.GitHubTrendingService.get_trending_repos')
    def test_get_trending_repos_service_error(self, mock_get_trending_repos):
        """Test handling of service error."""
        async def run_test():
            mock_get_trending_repos.side_effect = ValueError("Service Error")

            with self.assertRaises(ValueError):
                await self.agent.get_trending_repos()
        
        asyncio.run(run_test())

    def test_get_trending_repos_return_type(self):
        """Test that get_trending_repos returns a list of dictionaries."""
        async def run_test():
            with patch('app.services.github_trending_service.GitHubTrendingService.get_trending_repos') as mock_get_trending_repos:
                mock_get_trending_repos.return_value = [
                    {
                        'name': 'test-repo1',
                        'description': 'Test description',
                        'language': 'Python',
                        'stars': '100',
                        'url': 'https://github.com/test-repo1'
                    },
                    {
                        'name': 'test-repo2',
                        'description': 'Another test',
                        'language': 'JavaScript',
                        'stars': '50',
                        'url': 'https://github.com/test-repo2'
                    }
                ]

                result = await self.agent.get_trending_repos()
                self.assertIsInstance(result, list)
                self.assertTrue(all(isinstance(repo, dict) for repo in result))
                self.assertTrue(all('name' in repo for repo in result))
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
