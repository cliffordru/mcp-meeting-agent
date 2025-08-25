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
from ..schemas.meeting_info import MeetingInfo
from ..schemas.tech_trivia import TechTriviaQuestion
from ..schemas.fun_facts import FunFact
from ..formatters.repository_formatter import RepositoryFormatter
from ..prompts.meeting_prompts import MeetingPrompts

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

    async def format_meeting_info(self, trivia_question: TechTriviaQuestion, fun_fact: FunFact, trending_repos: list[dict]) -> MeetingInfo:
        """
        Formats structured data from the three agents into meeting notes for the host.
        """
        try:
            # Use the repository formatter for trending repos
            trending_repos_text = RepositoryFormatter.format_trending_repos_for_llm(trending_repos)
            
            # Use the prompt template
            prompt = MeetingPrompts.format_meeting_info_prompt(
                trivia_question.question,
                trivia_question.correct_answer,
                fun_fact.text,
                trending_repos_text
            )
            
            summary = await self.get_string_response(prompt)
            
            return MeetingInfo(
                trivia_question=trivia_question.question,
                trivia_answer=trivia_question.correct_answer,
                fun_fact=fun_fact.text,
                trending_repos=[repo.get('name', str(repo)) if isinstance(repo, dict) else str(repo) for repo in trending_repos],
                summary=summary
            )
            
        except Exception as e:
            logger.error("Error formatting meeting info", error=str(e))
            raise

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
