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
                    validated_fact = ta.validate_python(await response.json())
                    
                    return validated_fact
                        
            except (aiohttp.ClientError, ValidationError) as e:
                logger.error(
                    "Error fetching or validating fun fact",
                    error=str(e),
                    exc_info=True
                )
                raise ValueError(f"Could not retrieve valid fun fact data: {str(e)}") from e
            except Exception as e:
                logger.error(
                    "Unexpected error while fetching fun fact",
                    error=str(e),
                    exc_info=True
                )
                raise ValueError(f"An error occurred while fetching fun fact: {str(e)}") from e
