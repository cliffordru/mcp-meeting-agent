"""
Provides a service for interacting with the Fun Facts API.
"""
import aiohttp
from pydantic import ValidationError, TypeAdapter

from ..core.config import settings
from ..core.logging_config import get_logger
from ..schemas.fun_facts import FunFact

logger = get_logger(__name__)


class FunFactsService:
    """A service class for handling Fun Facts API interactions."""

    def __init__(self):
        self.api_url = settings.FUN_FACTS_API_URL
        self.timeout = settings.API_TIMEOUT

    async def get_fun_fact(self) -> FunFact:
        """
        Fetches and validates a fun fact from the API.

        Returns:
            A FunFact object.
        """
        async with aiohttp.ClientSession() as client:
            try:
                async with client.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()

                    # Validate the response against the Pydantic model
                    ta = TypeAdapter(FunFact)
                    validated_response = ta.validate_python(await response.json())

                    logger.info("Successfully fetched fun fact from API")
                    return validated_response

            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limited
                    logger.warning("Fun facts API rate limited, using fallback response")
                    return self._get_fallback_fact()
                logger.error(
                    "Error fetching fun fact",
                    error=str(e),
                    status_code=e.status,
                    url=self.api_url
                )
                return self._get_fallback_fact()
            except (aiohttp.ClientError, ValidationError) as e:
                logger.error(
                    "Error fetching or validating fun fact",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_fact()
            except Exception as e:
                logger.error(
                    "Unexpected error while fetching fun fact",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_fact()

    def _get_fallback_fact(self) -> FunFact:
        """Returns a fallback fun fact when the API is unavailable."""
        logger.info("Using fallback fun fact")
        return FunFact(
            text="The average person spends 6 months of their life waiting for red lights."
        )
