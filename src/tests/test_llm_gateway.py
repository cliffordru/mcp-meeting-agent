"""Tests for the LLMGateway class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.core.llm_gateway import LLMGateway
from app.schemas.meeting_info import MeetingInfo
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact


class TestLLMGateway(unittest.TestCase):
    """Test cases for LLMGateway."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('app.core.llm_gateway.settings') as mock_settings:
            mock_settings.LLM_MODEL = 'test-model'
            mock_settings.LLM_API_KEY.get_secret_value.return_value = 'test-key'
            mock_settings.LLM_API_BASE_URL = 'https://test-api.com'
            self.gateway = LLMGateway()

    def test_init(self):
        """Test LLMGateway initialization."""
        with patch('app.core.llm_gateway.settings') as mock_settings:
            mock_settings.LLM_MODEL = 'test-model'
            mock_settings.LLM_API_KEY.get_secret_value.return_value = 'test-key'
            mock_settings.LLM_API_BASE_URL = 'https://test-api.com'
            
            gateway = LLMGateway()
            self.assertIsInstance(gateway, LLMGateway)
            self.assertIsNotNone(gateway.chat_model)

    @patch('app.core.llm_gateway.LLMGateway.get_string_response')
    def test_format_meeting_info_success(self, mock_get_string_response):
        """Test successful meeting info formatting."""
        async def run_test():
            # Mock the LLM response
            mock_get_string_response.return_value = "Here's your meeting summary..."
            
            # Create test data
            trivia_question = TechTriviaQuestion(
                category="Science: Computers",
                type="multiple",
                difficulty="medium",
                question="What is Python?",
                correct_answer="Programming language",
                incorrect_answers=["Snake", "Game", "Database"]
            )
            
            fun_fact = FunFact(
                id="123",
                text="Python was named after Monty Python",
                source="Test Source",
                source_url="https://test.com",
                language="en",
                permalink="https://test.com/fact/123"
            )
            
            trending_repos = ["repo1", "repo2", "repo3"]
            
            result = await self.gateway.format_meeting_info(
                trivia_question, fun_fact, trending_repos
            )
            
            self.assertIsInstance(result, MeetingInfo)
            self.assertEqual(result.trivia_question, "What is Python?")
            self.assertEqual(result.trivia_answer, "Programming language")
            self.assertEqual(result.fun_fact, "Python was named after Monty Python")
            self.assertEqual(result.trending_repos, ["repo1", "repo2", "repo3"])
            self.assertEqual(result.summary, "Here's your meeting summary...")
        
        asyncio.run(run_test())

    @patch('app.core.llm_gateway.LLMGateway.get_string_response')
    def test_format_meeting_info_llm_error(self, mock_get_string_response):
        """Test handling of LLM error during formatting."""
        async def run_test():
            mock_get_string_response.side_effect = ValueError("LLM Error")
            
            trivia_question = TechTriviaQuestion(
                category="Science: Computers",
                type="multiple",
                difficulty="medium",
                question="What is Python?",
                correct_answer="Programming language",
                incorrect_answers=["Snake", "Game", "Database"]
            )
            
            fun_fact = FunFact(
                id="123",
                text="Python was named after Monty Python",
                source="Test Source",
                source_url="https://test.com",
                language="en",
                permalink="https://test.com/fact/123"
            )
            
            trending_repos = ["repo1", "repo2", "repo3"]
            
            with self.assertRaises(ValueError):
                await self.gateway.format_meeting_info(
                    trivia_question, fun_fact, trending_repos
                )
        
        asyncio.run(run_test())

    def test_get_string_response_success(self):
        """Test successful string response from LLM."""
        async def run_test():
            with patch.object(self.gateway, 'chat_model') as mock_chat_model:
                mock_response = Mock()
                mock_response.content = "Test response from LLM"
                mock_chat_model.ainvoke = AsyncMock(return_value=mock_response)
                
                result = await self.gateway.get_string_response("Test prompt")
                
                self.assertEqual(result, "Test response from LLM")
                mock_chat_model.ainvoke.assert_called_once_with("Test prompt")
        
        asyncio.run(run_test())

    def test_get_string_response_error(self):
        """Test handling of LLM error."""
        async def run_test():
            with patch.object(self.gateway, 'chat_model') as mock_chat_model:
                mock_chat_model.ainvoke.side_effect = Exception("LLM Error")
                
                with self.assertRaises(ValueError):
                    await self.gateway.get_string_response("Test prompt")
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
