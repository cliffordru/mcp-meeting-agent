"""
Provides a gateway for interacting with a Large Language Model (LLM).
"""
from typing import Optional, Type, TypeVar

from langchain_core.callbacks import CallbackManager
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler
from pydantic import BaseModel

from .config import settings
from .logging_config import get_logger

T = TypeVar('T', bound=BaseModel)
logger = get_logger(__name__)

class LLMGateway:
    """A gateway class for handling interactions with the configured LLM."""
    
    def __init__(self, langfuse_callback: Optional[CallbackHandler] = None):
        logger.info(
            "Initializing LLMGateway",
            model=settings.LLM_MODEL,
            base_url=settings.LLM_API_BASE_URL
        )
        self.chat_model = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY.get_secret_value(),
            base_url=settings.LLM_API_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            callback_manager=CallbackManager([langfuse_callback]) if langfuse_callback else None,
            request_timeout=settings.LLM_REQUEST_TIMEOUT,
        )

    async def get_string_response(self, prompt: str) -> str:
        """
        Sends a prompt to the LLM and returns a simple string response.
        """
        try:
            result = await self.chat_model.ainvoke(prompt)
            return result.content
        except Exception as e:
            logger.error(
                "Error getting string response from LLM",
                error=str(e),
                model=self.chat_model.model_name
            )
            raise ValueError(f"Failed to get a valid response from the LLM: {str(e)}")

    async def get_structured_response(self, prompt: str, response_model: Type[T]) -> T:
        """
        Sends a prompt to the LLM and returns a validated Pydantic model using
        the recommended Pydantic v2 method.
        """
        try:
            structured_model = self.chat_model.with_structured_output(response_model)
            result = await structured_model.ainvoke(prompt)
            return result
        except Exception as e:
            logger.error(
                "Error getting structured response from LLM",
                error=str(e),
                model=self.chat_model.model_name
            )
            raise ValueError(f"Failed to get a valid structured response from the LLM: {str(e)}")
