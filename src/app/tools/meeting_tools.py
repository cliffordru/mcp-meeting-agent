"""
LangChain tools for meeting preparation functionality.
"""
from langchain.tools import tool
from ..services.tech_trivia_service import TechTriviaService
from ..services.fun_facts_service import FunFactsService
from ..services.github_trending_service import GitHubTrendingService
from ..formatters.repository_formatter import RepositoryFormatter
from ..core.logging_config import get_logger

logger = get_logger(__name__)


@tool
async def get_tech_trivia() -> str:
    """Get a technology trivia question and answer for meeting icebreakers."""
    try:
        service = TechTriviaService()
        trivia = await service.get_tech_trivia()
        return f"Question: {trivia.question}\nAnswer: {trivia.correct_answer}"
    except Exception as e:
        logger.error("Error getting tech trivia", error=str(e))
        # Provide a fallback trivia question
        return "Question: What programming language was created by Guido van Rossum?\nAnswer: Python"


@tool
async def get_fun_fact() -> str:
    """Get an interesting fun fact for meeting engagement."""
    try:
        service = FunFactsService()
        fact = await service.get_fun_fact()
        return fact.text
    except Exception as e:
        logger.error("Error getting fun fact", error=str(e))
        # Provide a fallback fun fact
        return "Did you know? The average person spends 6 months of their life waiting for red lights."


@tool
async def get_trending_repos() -> str:
    """Get current trending GitHub repositories for tech discussions."""
    try:
        service = GitHubTrendingService()
        repos = await service.get_trending_repos()
        return RepositoryFormatter.format_trending_repos_for_llm(repos)
    except Exception as e:
        logger.error("Error getting trending repos", error=str(e))
        # Provide fallback trending repos
        return """• langchain-ai/langchain - Building applications with LLMs through composability
• openai/openai-python - The official Python library for the OpenAI API
• microsoft/vscode - Visual Studio Code is a code editor redefined and optimized for building and debugging modern web and cloud applications"""
