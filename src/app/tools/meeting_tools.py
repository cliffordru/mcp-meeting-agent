"""
LangChain tools for meeting preparation functionality.
"""
from langchain.tools import tool
from ..services.tech_trivia_service import TechTriviaService
from ..services.fun_facts_service import FunFactsService
from ..services.github_trending_service import GitHubTrendingService
from ..formatters.repository_formatter import RepositoryFormatter
from ..core.logging_config import get_logger
from ..prompts.fallback_prompts import (
    TECH_TRIVIA_FALLBACK_PROMPT,
    FUN_FACT_FALLBACK_PROMPT,
    TRENDING_REPOS_FALLBACK_PROMPT
)

logger = get_logger(__name__)


@tool
async def get_tech_trivia(ctx=None) -> str:
    """Get a technology trivia question and answer for meeting icebreakers with LLM fallback."""
    try:
        service = TechTriviaService()
        trivia = await service.get_tech_trivia()
        return f"Question: {trivia.question}\nAnswer: {trivia.correct_answer}"
    except Exception as e:
        logger.error("Error getting tech trivia", error=str(e))
        
        # If we have MCP context, use LLM to generate contextual fallback
        if ctx:
            try:
                # Use MCP context to sample from LLM for dynamic fallback
                response = await ctx.sample(
                    model="gpt-4o-mini",
                    messages=TECH_TRIVIA_FALLBACK_PROMPT.format_messages(),
                    max_tokens=150
                )
                return response.content
            except Exception as llm_error:
                logger.error("Error generating LLM fallback", error=str(llm_error))
        
        # Fallback to hardcoded content if LLM generation fails
        return "Question: What programming language was created by Guido van Rossum?\nAnswer: Python"


@tool
async def get_fun_fact(ctx=None) -> str:
    """Get an interesting fun fact for meeting engagement with LLM fallback."""
    try:
        service = FunFactsService()
        fact = await service.get_fun_fact()
        return fact.text
    except Exception as e:
        logger.error("Error getting fun fact", error=str(e))
        
        # If we have MCP context, use LLM to generate contextual fallback
        if ctx:
            try:
                # Use MCP context to sample from LLM for dynamic fallback
                response = await ctx.sample(
                    model="gpt-4o-mini",
                    messages=FUN_FACT_FALLBACK_PROMPT.format_messages(),
                    max_tokens=100
                )
                return response.content
            except Exception as llm_error:
                logger.error("Error generating LLM fallback", error=str(llm_error))
        
        # Fallback to hardcoded content if LLM generation fails
        return "Did you know? The average person spends 6 months of their life waiting for red lights."


@tool
async def get_trending_repos(ctx=None) -> str:
    """Get current trending GitHub repositories for tech discussions with LLM fallback."""
    try:
        service = GitHubTrendingService()
        repos = await service.get_trending_repos()
        return RepositoryFormatter.format_trending_repos_for_llm(repos)
    except Exception as e:
        logger.error("Error getting trending repos", error=str(e))
        
        # If we have MCP context, use LLM to generate contextual fallback
        if ctx:
            try:
                # Use MCP context to sample from LLM for dynamic fallback
                response = await ctx.sample(
                    model="gpt-4o-mini",
                    messages=TRENDING_REPOS_FALLBACK_PROMPT.format_messages(),
                    max_tokens=200
                )
                return response.content
            except Exception as llm_error:
                logger.error("Error generating LLM fallback", error=str(llm_error))
        
        # Fallback to hardcoded content if LLM generation fails
        return """• langchain-ai/langchain - Building applications with LLMs through composability
• openai/openai-python - The official Python library for the OpenAI API
• microsoft/vscode - Visual Studio Code is a code editor redefined and optimized for building and debugging modern web and cloud applications"""
