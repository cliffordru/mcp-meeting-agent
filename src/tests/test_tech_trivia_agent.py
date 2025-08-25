"""Tests for the TechTriviaAgent class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.agents.tech_trivia_agent import TechTriviaAgent
from app.schemas.tech_trivia import TechTriviaQuestion


class TestTechTriviaAgent(unittest.TestCase):
    """Test cases for TechTriviaAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = TechTriviaAgent()

    def test_init(self):
        """Test TechTriviaAgent initialization."""
        agent = TechTriviaAgent()
        self.assertIsInstance(agent, TechTriviaAgent)
        self.assertIsNotNone(agent._service)

    @patch('app.services.tech_trivia_service.TechTriviaService.get_tech_trivia')
    def test_get_tech_trivia_success(self, mock_get_tech_trivia):
        """Test successful tech trivia retrieval."""
        async def run_test():
            # Mock the service response
            mock_trivia_question = TechTriviaQuestion(
                category="Science: Computers",
                type="multiple",
                difficulty="medium",
                question="What is the primary function of RAM in a computer?",
                correct_answer="Temporary data storage",
                incorrect_answers=["Permanent data storage", "CPU processing", "Graphics rendering"]
            )
            mock_get_tech_trivia.return_value = mock_trivia_question

            result = await self.agent.get_tech_trivia()

            self.assertIsInstance(result, TechTriviaQuestion)
            self.assertEqual(result.question, "What is the primary function of RAM in a computer?")
            self.assertEqual(result.correct_answer, "Temporary data storage")
            self.assertEqual(result.category, "Science: Computers")
        
        asyncio.run(run_test())

    @patch('app.services.tech_trivia_service.TechTriviaService.get_tech_trivia')
    def test_get_tech_trivia_service_error(self, mock_get_tech_trivia):
        """Test handling of service error."""
        async def run_test():
            mock_get_tech_trivia.side_effect = ValueError("Service Error")

            with self.assertRaises(ValueError):
                await self.agent.get_tech_trivia()
        
        asyncio.run(run_test())

    def test_get_tech_trivia_return_type(self):
        """Test that get_tech_trivia returns a TechTriviaQuestion object."""
        async def run_test():
            with patch('app.services.tech_trivia_service.TechTriviaService.get_tech_trivia') as mock_get_tech_trivia:
                mock_get_tech_trivia.return_value = TechTriviaQuestion(
                    category="Science: Computers",
                    type="multiple",
                    difficulty="easy",
                    question="Test question?",
                    correct_answer="Test answer",
                    incorrect_answers=["Wrong 1", "Wrong 2", "Wrong 3"]
                )

                result = await self.agent.get_tech_trivia()
                self.assertIsInstance(result, TechTriviaQuestion)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
