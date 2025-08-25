"""
Services package for handling external API interactions.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import aiohttp
from pydantic import ValidationError, TypeAdapter

from ..core.config import settings
from ..core.logging_config import get_logger

logger = get_logger(__name__)


class BaseService(ABC):
    """Base service class providing common HTTP client functionality and error handling."""
    
    def __init__(self, api_url: str, timeout: Optional[int] = None):
        self.api_url = api_url
        self.timeout = timeout or settings.API_TIMEOUT
    
    async def _make_request(self, response_model: Optional[Any] = None) -> Any:
        """
        Make an HTTP GET request with common error handling and validation.
        
        Args:
            response_model: Optional Pydantic model to validate the response against
            
        Returns:
            The validated response data or fallback data
        """
        async with aiohttp.ClientSession() as client:
            try:
                async with client.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Validate against Pydantic model if provided
                    if response_model:
                        ta = TypeAdapter(response_model)
                        validated_data = ta.validate_python(data)
                        logger.info(f"Successfully fetched data from {self.api_url}")
                        return validated_data
                    
                    logger.info(f"Successfully fetched data from {self.api_url}")
                    return data
                    
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limited
                    logger.warning(f"API rate limited for {self.api_url}, using fallback")
                    return self._get_fallback_data()
                    
                logger.error(
                    f"HTTP error fetching from {self.api_url}",
                    error=str(e),
                    status_code=e.status,
                    url=self.api_url
                )
                return self._get_fallback_data()
                
            except (aiohttp.ClientError, ValidationError) as e:
                logger.error(
                    f"Error fetching or validating data from {self.api_url}",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_data()
                
            except Exception as e:
                logger.error(
                    f"Unexpected error while fetching from {self.api_url}",
                    error=str(e),
                    url=self.api_url
                )
                return self._get_fallback_data()
    
    @abstractmethod
    def _get_fallback_data(self) -> Any:
        """Return fallback data when the API is unavailable. Must be implemented by subclasses."""
        pass
