"""
Provides a gateway for interacting with a Large Language Model (LLM).
"""
from typing import Optional, Type, TypeVar

from langchain_core.callbacks import CallbackManager
from langchain_core.language_models.chat_models import BaseChatModel
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
        
        # Create provider-agnostic chat model based on configuration
        self.chat_model = self._create_chat_model(langfuse_callback)

    def _create_chat_model(self, langfuse_callback: Optional[CallbackHandler] = None) -> BaseChatModel:
        """
        Create a provider-agnostic chat model based on configuration.
        
        Supports:
        - OpenAI/OpenRouter (via base_url)
        - Anthropic Claude (requires langchain-anthropic)
        - Google Gemini (requires langchain-google-genai)
        - Other providers via base_url configuration
        """
        callback_manager = CallbackManager([langfuse_callback]) if langfuse_callback else None
        
        # Common parameters for all providers
        common_params = {
            "temperature": settings.LLM_TEMPERATURE,
            "callback_manager": callback_manager,
            "request_timeout": settings.LLM_REQUEST_TIMEOUT,
        }
        
        # Determine provider based on model name and base URL
        model_name = settings.LLM_MODEL.lower() if settings.LLM_MODEL else ""
        
        # Anthropic Claude models
        if model_name.startswith(("claude-", "claude")):
            logger.info("Using Anthropic Claude provider")
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=settings.LLM_MODEL,
                    api_key=settings.LLM_API_KEY.get_secret_value(),
                    **common_params
                )
            except ImportError:
                raise ImportError(
                    "Anthropic Claude support requires 'langchain-anthropic' package. "
                    "Install with: uv add langchain-anthropic"
                )
        
        # Google Gemini models
        elif model_name.startswith(("gemini-", "gemini")):
            logger.info("Using Google Gemini provider")
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=settings.LLM_MODEL,
                    google_api_key=settings.LLM_API_KEY.get_secret_value(),
                    **common_params
                )
            except ImportError:
                raise ImportError(
                    "Google Gemini support requires 'langchain-google-genai' package. "
                    "Install with: uv add langchain-google-genai"
                )
        
        # OpenAI/OpenRouter or other providers via base_url
        else:
            logger.info("Using OpenAI/OpenRouter or custom provider via base_url")
            return ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.LLM_API_KEY.get_secret_value(),
                base_url=settings.LLM_API_BASE_URL,
                **common_params
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
