"""Tests for the PlannerAgent class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.agents.planner_agent import PlannerAgent
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact
from app.schemas.meeting_info import MeetingInfo


class TestPlannerAgent(unittest.TestCase):
    """Test cases for PlannerAgent."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('app.core.llm_gateway.settings') as mock_settings:
            mock_settings.LLM_MODEL = 'test-model'
            mock_settings.LLM_API_KEY.get_secret_value.return_value = 'test-key'
            mock_settings.LLM_API_BASE_URL = 'https://test-api.com'
            self.agent = PlannerAgent()

    def test_init(self):
        """Test PlannerAgent initialization."""
        with patch('app.core.llm_gateway.settings') as mock_settings:
            mock_settings.LLM_MODEL = 'test-model'
            mock_settings.LLM_API_KEY.get_secret_value.return_value = 'test-key'
            mock_settings.LLM_API_BASE_URL = 'https://test-api.com'
            
            agent = PlannerAgent()
            self.assertIsInstance(agent, PlannerAgent)
            self.assertIsNotNone(agent.llm_gateway)

    @patch('app.agents.planner_agent.GitHubTrendingAgent.get_trending_repos')
    @patch('app.agents.planner_agent.FunFactsAgent.get_fun_fact')
    @patch('app.agents.planner_agent.TechTriviaAgent.get_tech_trivia')
    @patch('app.core.llm_gateway.LLMGateway.format_meeting_info')
    def test_plan_meeting_async_success(self, mock_format_meeting_info, mock_get_tech_trivia, mock_get_fun_fact, mock_get_trending_repos):
        """Test successful async meeting planning."""
        async def run_test():
            # Mock the agent responses
            mock_trivia_question = TechTriviaQuestion(
                category="Science: Computers",
                type="multiple",
                difficulty="medium",
                question="What is Python?",
                correct_answer="Programming language",
                incorrect_answers=["Snake", "Game", "Database"]
            )
            mock_get_tech_trivia.return_value = mock_trivia_question
            
            mock_fun_fact = FunFact(
                id="123",
                text="Python was named after Monty Python",
                source="Test Source",
                source_url="https://test.com",
                language="en",
                permalink="https://test.com/fact/123"
            )
            mock_get_fun_fact.return_value = mock_fun_fact
            
            mock_trending_repos = [
                {
                    'name': 'repo1',
                    'description': 'Test repository 1',
                    'language': 'Python',
                    'stars': '100',
                    'url': 'https://github.com/repo1'
                },
                {
                    'name': 'repo2',
                    'description': 'Test repository 2',
                    'language': 'JavaScript',
                    'stars': '50',
                    'url': 'https://github.com/repo2'
                },
                {
                    'name': 'repo3',
                    'description': 'Test repository 3',
                    'language': 'TypeScript',
                    'stars': '75',
                    'url': 'https://github.com/repo3'
                }
            ]
            mock_get_trending_repos.return_value = mock_trending_repos
            
            # Mock the LLM gateway response
            mock_meeting_info = MeetingInfo(
                trivia_question="What is Python?",
                trivia_answer="Programming language",
                fun_fact="Python was named after Monty Python",
                trending_repos=["repo1", "repo2", "repo3"],
                summary="Here's your meeting summary..."
            )
            mock_format_meeting_info.return_value = mock_meeting_info
            
            result = await self.agent.plan_meeting_async()
            
            self.assertEqual(result, "Here's your meeting summary...")
            
            # Verify all agents were called
            mock_get_tech_trivia.assert_called_once()
            mock_get_fun_fact.assert_called_once()
            mock_get_trending_repos.assert_called_once()
            mock_format_meeting_info.assert_called_once_with(
                mock_trivia_question, mock_fun_fact, mock_trending_repos
            )
        
        asyncio.run(run_test())

    @patch('app.agents.planner_agent.GitHubTrendingAgent.get_trending_repos')
    @patch('app.agents.planner_agent.FunFactsAgent.get_fun_fact')
    @patch('app.agents.planner_agent.TechTriviaAgent.get_tech_trivia')
    def test_plan_meeting_async_fallback(self, mock_get_tech_trivia, mock_get_fun_fact, mock_get_trending_repos):
        """Test fallback behavior when LLM gateway fails."""
        async def run_test():
            # Mock the agent responses
            mock_trivia_question = TechTriviaQuestion(
                category="Science: Computers",
                type="multiple",
                difficulty="medium",
                question="What is Python?",
                correct_answer="Programming language",
                incorrect_answers=["Snake", "Game", "Database"]
            )
            mock_get_tech_trivia.return_value = mock_trivia_question
            
            mock_fun_fact = FunFact(
                id="123",
                text="Python was named after Monty Python",
                source="Test Source",
                source_url="https://test.com",
                language="en",
                permalink="https://test.com/fact/123"
            )
            mock_get_fun_fact.return_value = mock_fun_fact
            
            mock_trending_repos = [
                {
                    'name': 'repo1',
                    'description': 'Test repository 1',
                    'language': 'Python',
                    'stars': '100',
                    'url': 'https://github.com/repo1'
                },
                {
                    'name': 'repo2',
                    'description': 'Test repository 2',
                    'language': 'JavaScript',
                    'stars': '50',
                    'url': 'https://github.com/repo2'
                },
                {
                    'name': 'repo3',
                    'description': 'Test repository 3',
                    'language': 'TypeScript',
                    'stars': '75',
                    'url': 'https://github.com/repo3'
                }
            ]
            mock_get_trending_repos.return_value = mock_trending_repos
            
            # Mock LLM gateway to fail
            with patch.object(self.agent.llm_gateway, 'format_meeting_info', side_effect=Exception("LLM Error")):
                result = await self.agent.plan_meeting_async()
                
                # Should return fallback message in meeting notes format
                self.assertIn("Meeting Notes for Host", result)
                self.assertIn("What is Python?", result)
                self.assertIn("Programming language", result)
                self.assertIn("Python was named after Monty Python", result)
                self.assertIn("repo1", result)
                self.assertIn("Test repository 1", result)
                self.assertIn("https://github.com/repo1", result)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
