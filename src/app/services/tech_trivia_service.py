"""
Provides a service for interacting with the Tech Trivia API.
"""
from typing import List

import aiohttp

from pydantic import ValidationError, TypeAdapter

from ..core.config import settings
from ..core.logging_config import get_logger
from ..schemas.tech_trivia import TechTriviaResponse, TechTriviaQuestion

logger = get_logger(__name__)


class TechTriviaService:
    """A service class for handling Tech Trivia API interactions."""

    def __init__(self):
        self.api_url = settings.TECH_TRIVIA_API_URL
        self.timeout = settings.API_TIMEOUT

    async def get_tech_trivia(self) -> TechTriviaQuestion:
        """
        Fetches and validates a tech trivia question from the API.

        Returns:
            A TechTriviaQuestion object.
        """
        async with aiohttp.ClientSession() as client:
            try:
                async with client.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()

                    # Validate the response against the Pydantic model
                    ta = TypeAdapter(TechTriviaResponse)
                    validated_response = ta.validate_python(await response.json())

                    # Return the first question from the results
                    if validated_response.results:
                        logger.info("Successfully fetched tech trivia from API")
                        return validated_response.results[0]
                    raise ValueError("No trivia questions found in response")

            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limited
                    logger.warning("Tech trivia API rate limited, using fallback response")
                    return self._get_fallback_trivia()
                logger.error(
                    "Error fetching tech trivia",
                    error=str(e),
                    status_code=e.status,
                    url=self.api_url
                )
                return self._get_fallback_trivia()
            except (aiohttp.ClientError, ValidationError) as e:
                logger.error(
                    "Error fetching or validating tech trivia",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_trivia()
            except Exception as e:
                logger.error(
                    "Unexpected error while fetching tech trivia",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_trivia()

    def _get_fallback_trivia(self) -> TechTriviaQuestion:
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
