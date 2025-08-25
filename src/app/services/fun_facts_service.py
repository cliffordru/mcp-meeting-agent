"""
Provides a service for interacting with the Fun Facts API.
"""
from ..schemas.fun_facts import FunFact
from . import BaseService
from ..core.logging_config import get_logger
from ..core.config import settings

logger = get_logger(__name__)


class FunFactsService(BaseService):
    """A service class for handling Fun Facts API interactions."""

    def __init__(self):
        super().__init__(settings.FUN_FACTS_API_URL)

    async def get_fun_fact(self) -> FunFact:
        """
        Fetches and validates a fun fact from the API.

        Returns:
            A FunFact object.
        """
        response = await self._make_request(FunFact)
        
        # Handle the response structure
        if hasattr(response, 'text'):
            return response
        elif isinstance(response, dict) and response.get('text'):
            # Handle case where response is a dict
            return FunFact(**response)
        else:
            logger.warning("Invalid fun fact response structure, using fallback")
            return self._get_fallback_data()

    def _get_fallback_data(self) -> FunFact:
        """Returns a fallback fun fact when the API is unavailable."""
        logger.info("Using fallback fun fact")
        return FunFact(
            text="The average person spends 6 months of their life waiting for red lights."
        )
