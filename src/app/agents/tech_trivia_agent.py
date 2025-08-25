"""
An agent responsible for fetching tech trivia questions.
"""
from typing import Optional

from ..services.tech_trivia_service import TechTriviaService
from ..schemas.tech_trivia import TechTriviaQuestion


class TechTriviaAgent:
    """
    Wraps the TechTriviaService to provide a clean interface for fetching trivia questions.
    """

    def __init__(self):
        self._service = TechTriviaService()

    async def get_tech_trivia(self) -> TechTriviaQuestion:
        """
        Fetches a tech trivia question.

        Returns:
            A TechTriviaQuestion object.
        """
        trivia_question = await self._service.get_tech_trivia()
        return trivia_question