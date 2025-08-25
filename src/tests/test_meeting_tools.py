"""
Tests for meeting tools.
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact
from app.tools.meeting_tools import get_tech_trivia, get_fun_fact, get_trending_repos


class TestMeetingTools:
    """Test cases for meeting tools."""

    @pytest.mark.asyncio
    async def test_get_tech_trivia_success(self):
        """Test successful tech trivia retrieval."""
        mock_trivia = TechTriviaQuestion(
            category="Science: Computers",
            type="multiple",
            difficulty="medium",
            question="What is Python?",
            correct_answer="A programming language",
            incorrect_answers=["A snake", "A game", "A database"]
        )
        
        with patch('app.tools.meeting_tools.TechTriviaService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_tech_trivia.return_value = mock_trivia
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_tech_trivia.coroutine()
            
            assert "Question: What is Python?" in result
            assert "Answer: A programming language" in result
            mock_service.get_tech_trivia.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tech_trivia_failure_with_llm_fallback(self):
        """Test tech trivia retrieval failure with LLM fallback."""
        with patch('app.tools.meeting_tools.TechTriviaService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_tech_trivia.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Mock MCP context with LLM sampling
            mock_ctx = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = "Question: What is the latest version of React?\nAnswer: React 18"
            mock_ctx.sample.return_value = mock_response
            
            # Call the underlying function directly with context
            result = await get_tech_trivia.coroutine(ctx=mock_ctx)
            
            # Should return LLM-generated fallback content
            assert "Question: What is the latest version of React?" in result
            assert "Answer: React 18" in result
            mock_ctx.sample.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tech_trivia_failure_without_context(self):
        """Test tech trivia retrieval failure without context (hardcoded fallback)."""
        with patch('app.tools.meeting_tools.TechTriviaService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_tech_trivia.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly without context
            result = await get_tech_trivia.coroutine()
            
            # Should return hardcoded fallback content
            assert "Question: What programming language was created by Guido van Rossum?" in result
            assert "Answer: Python" in result

    @pytest.mark.asyncio
    async def test_get_fun_fact_success(self):
        """Test successful fun fact retrieval."""
        mock_fact = FunFact(
            id="123",
            text="The average person spends 6 months of their lifetime waiting for red lights to turn green.",
            source="Useless Facts API",
            source_url="https://uselessfacts.jsph.pl/",
            language="en",
            permalink="https://uselessfacts.jsph.pl/fact/123"
        )
        
        with patch('app.tools.meeting_tools.FunFactsService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_fun_fact.return_value = mock_fact
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_fun_fact.coroutine()
            
            assert "The average person spends 6 months" in result
            mock_service.get_fun_fact.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_fun_fact_failure_with_llm_fallback(self):
        """Test fun fact retrieval failure with LLM fallback."""
        with patch('app.tools.meeting_tools.FunFactsService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_fun_fact.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Mock MCP context with LLM sampling
            mock_ctx = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = "Did you know? The first computer bug was an actual bug!"
            mock_ctx.sample.return_value = mock_response
            
            # Call the underlying function directly with context
            result = await get_fun_fact.coroutine(ctx=mock_ctx)
            
            # Should return LLM-generated fallback content
            assert "Did you know? The first computer bug was an actual bug!" in result
            mock_ctx.sample.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_trending_repos_success(self):
        """Test successful trending repos retrieval."""
        mock_repos = [
            {"name": "repo1", "description": "Test repo 1", "language": "Python", "stars": "1000", "url": "https://github.com/repo1"},
            {"name": "repo2", "description": "Test repo 2", "language": "JavaScript", "stars": "500", "url": "https://github.com/repo2"}
        ]
        
        with patch('app.tools.meeting_tools.GitHubTrendingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_trending_repos.return_value = mock_repos
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_trending_repos.coroutine()
            
            assert "repo1" in result
            assert "repo2" in result
            assert "Python" in result
            assert "JavaScript" in result
            mock_service.get_trending_repos.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_trending_repos_failure_with_llm_fallback(self):
        """Test trending repos retrieval failure with LLM fallback."""
        with patch('app.tools.meeting_tools.GitHubTrendingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_trending_repos.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Mock MCP context with LLM sampling
            mock_ctx = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = "• react/react - A JavaScript library for building user interfaces\n• vuejs/vue - Progressive JavaScript framework\n• angular/angular - Platform for building mobile and desktop web applications"
            mock_ctx.sample.return_value = mock_response
            
            # Call the underlying function directly with context
            result = await get_trending_repos.coroutine(ctx=mock_ctx)
            
            # Should return LLM-generated fallback content
            assert "react/react" in result
            assert "vuejs/vue" in result
            assert "angular/angular" in result
            mock_ctx.sample.assert_called_once()
