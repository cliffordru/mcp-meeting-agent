"""
LangChain tools for meeting preparation functionality.
"""
from langchain.tools import tool
from ..services.tech_trivia_service import TechTriviaService
from ..services.fun_facts_service import FunFactsService
from ..services.github_trending_service import GitHubTrendingService
from ..formatters.repository_formatter import RepositoryFormatter
from ..prompts.fallback_prompts import (
    TECH_TRIVIA_FALLBACK_PROMPT,
    FUN_FACT_FALLBACK_PROMPT,
    TRENDING_REPOS_FALLBACK_PROMPT
)
from . import tool_error_handler


@tool
@tool_error_handler(
    TECH_TRIVIA_FALLBACK_PROMPT,
    "Question: What programming language was created by Guido van Rossum?\nAnswer: Python"
)
async def get_tech_trivia(ctx=None) -> str:
    """Get a technology trivia question and answer for meeting icebreakers with LLM fallback."""
    service = TechTriviaService()
    trivia = await service.get_tech_trivia()
    return f"Question: {trivia.question}\nAnswer: {trivia.correct_answer}"


@tool
@tool_error_handler(
    FUN_FACT_FALLBACK_PROMPT,
    "Did you know? The average person spends 6 months of their life waiting for red lights."
)
async def get_fun_fact(ctx=None) -> str:
    """Get an interesting fun fact for meeting engagement with LLM fallback."""
    service = FunFactsService()
    fact = await service.get_fun_fact()
    return fact.text


@tool
@tool_error_handler(
    TRENDING_REPOS_FALLBACK_PROMPT,
    """• langchain-ai/langchain - Building applications with LLMs through composability
• openai/openai-python - The official Python library for the OpenAI API
• microsoft/vscode - Visual Studio Code is a code editor redefined and optimized for building and debugging modern web and cloud applications"""
)
async def get_trending_repos(ctx=None) -> str:
    """Get current trending GitHub repositories for tech discussions with LLM fallback."""
    service = GitHubTrendingService()
    repos = await service.get_trending_repos()
    return RepositoryFormatter.format_trending_repos_for_llm(repos)
