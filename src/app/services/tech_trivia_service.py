"""
Provides a service for interacting with the Tech Trivia API.
"""
from typing import List

from ..schemas.tech_trivia import TechTriviaResponse, TechTriviaQuestion
from . import BaseService
from ..core.logging_config import get_logger
from ..core.config import settings

logger = get_logger(__name__)


class TechTriviaService(BaseService):
    """A service class for handling Tech Trivia API interactions."""

    def __init__(self):
        super().__init__(settings.TECH_TRIVIA_API_URL)

    async def get_tech_trivia(self) -> TechTriviaQuestion:
        """
        Fetches and validates a tech trivia question from the API.

        Returns:
            A TechTriviaQuestion object.
        """
        response = await self._make_request(TechTriviaResponse)
        
        # Handle the response structure
        if hasattr(response, 'results') and response.results:
            return response.results[0]
        elif isinstance(response, dict) and response.get('results'):
            # Handle case where response is a dict
            return response['results'][0]
        else:
            logger.warning("No trivia questions found in response, using fallback")
            return self._get_fallback_data()

    def _get_fallback_data(self) -> TechTriviaQuestion:
        """Returns a fallback trivia question when the API is unavailable."""
        logger.info("Using fallback tech trivia question")
        return TechTriviaQuestion(
            category="Science: Computers",
            type="multiple",
            difficulty="medium",
            question="What programming language was created by Guido van Rossum?",
            correct_answer="Python",
            incorrect_answers=["Java", "C++", "JavaScript"]
        )
