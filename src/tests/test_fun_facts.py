"""Tests for the FunFactsAgent class."""

import unittest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from app.agents.fun_facts_agent import FunFactsAgent
from app.schemas.fun_facts import FunFact


class TestFunFactsAgent(unittest.TestCase):
    """Test cases for FunFactsAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = FunFactsAgent()

    def test_init(self):
        """Test FunFactsAgent initialization."""
        agent = FunFactsAgent()
        self.assertIsInstance(agent, FunFactsAgent)
        self.assertIsNotNone(agent._service)

    @patch('app.services.fun_facts_service.FunFactsService.get_fun_fact')
    def test_get_fun_fact_success(self, mock_get_fun_fact):
        """Test successful fun fact retrieval."""
        async def run_test():
            # Mock the service response
            mock_fun_fact = FunFact(
                id="123",
                text="A fun fact about programming",
                source="Test Source",
                source_url="https://test.com",
                language="en",
                permalink="https://test.com/fact/123"
            )
            mock_get_fun_fact.return_value = mock_fun_fact

            result = await self.agent.get_fun_fact()

            self.assertIsInstance(result, FunFact)
            self.assertEqual(result.text, "A fun fact about programming")
            self.assertEqual(result.id, "123")
        
        asyncio.run(run_test())

    @patch('app.services.fun_facts_service.FunFactsService.get_fun_fact')
    def test_get_fun_fact_service_error(self, mock_get_fun_fact):
        """Test handling of service error."""
        async def run_test():
            mock_get_fun_fact.side_effect = ValueError("Service Error")

            with self.assertRaises(ValueError):
                await self.agent.get_fun_fact()
        
        asyncio.run(run_test())

    def test_get_fun_fact_return_type(self):
        """Test that get_fun_fact returns a FunFact object."""
        async def run_test():
            with patch('app.services.fun_facts_service.FunFactsService.get_fun_fact') as mock_get_fun_fact:
                mock_get_fun_fact.return_value = FunFact(
                    id="123",
                    text="Test fact",
                    source="Test Source",
                    source_url="https://test.com",
                    language="en",
                    permalink="https://test.com/fact/123"
                )

                result = await self.agent.get_fun_fact()
                self.assertIsInstance(result, FunFact)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
