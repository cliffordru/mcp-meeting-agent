"""
Tests for meeting tools.
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.tools.meeting_tools import get_tech_trivia, get_fun_fact, get_trending_repos
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact


class TestMeetingTools:
    """Test cases for meeting tools."""

    @pytest.mark.asyncio
    async def test_get_tech_trivia_success(self):
        """Test successful tech trivia retrieval."""
        mock_trivia = TechTriviaQuestion(
            category="Science: Computers",
            type="multiple",
            difficulty="easy",
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
    async def test_get_tech_trivia_failure(self):
        """Test tech trivia retrieval failure."""
        with patch('app.tools.meeting_tools.TechTriviaService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_tech_trivia.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_tech_trivia.coroutine()
            
            assert "Unable to fetch tech trivia" in result

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
    async def test_get_fun_fact_failure(self):
        """Test fun fact retrieval failure."""
        with patch('app.tools.meeting_tools.FunFactsService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_fun_fact.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_fun_fact.coroutine()
            
            assert "Unable to fetch fun fact" in result

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
    async def test_get_trending_repos_failure(self):
        """Test trending repos retrieval failure."""
        with patch('app.tools.meeting_tools.GitHubTrendingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_trending_repos.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service
            
            # Call the underlying function directly
            result = await get_trending_repos.coroutine()
            
            assert "Unable to fetch trending repositories" in result
