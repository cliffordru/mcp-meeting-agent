"""
Agent tools that wrap agent classes with LLM reasoning capabilities.
These tools provide intelligent improvement of the basic service data.
"""
from langchain.tools import tool
from ..agents.tech_trivia_agent import TechTriviaAgent
from ..agents.fun_facts_agent import FunFactsAgent
from ..agents.github_trending_agent import GitHubTrendingAgent
from ..core.llm_gateway import LLMGateway
from ..core.logging_config import get_logger
from ..prompts.agent_prompts import TECH_TRIVIA_ENHANCEMENT_PROMPT, FUN_FACT_ENHANCEMENT_PROMPT, TRENDING_ENHANCEMENT_PROMPT

logger = get_logger(__name__)


@tool
async def tech_trivia_agent(ctx=None, meeting_context: str = "") -> str:
    """
    Get tech trivia using the TechTriviaAgent with LLM reasoning.
    This agent can select and improve trivia based on the meeting context.
    """
    try:
        # Get basic trivia from the agent
        agent = TechTriviaAgent()
        trivia = await agent.get_tech_trivia()
        
        # If we have MCP context, improve with LLM reasoning
        if ctx and meeting_context:
            try:
                llm = LLMGateway().chat_model
                improvement_prompt = TECH_TRIVIA_ENHANCEMENT_PROMPT.format(
                    question=trivia.question,
                    answer=trivia.correct_answer,
                    meeting_context=meeting_context
                )
                
                response = await llm.ainvoke([{"role": "user", "content": improvement_prompt}])
                return response.content
            except Exception as e:
                logger.warning(f"Failed to improve trivia with LLM: {e}")
        
        # Return basic trivia if improvement fails
        return f"Question: {trivia.question}\nAnswer: {trivia.correct_answer}"
        
    except Exception as e:
        logger.error(f"Error in tech trivia agent: {e}")
        return "Unable to fetch tech trivia at this time."


@tool
async def fun_facts_agent(ctx=None, meeting_context: str = "") -> str:
    """
    Get fun facts using the FunFactsAgent with LLM reasoning.
    This agent can contextualize fun facts based on the meeting context.
    """
    try:
        # Get basic fun fact from the agent
        agent = FunFactsAgent()
        fun_fact = await agent.get_fun_fact()
        
        # If we have MCP context, improve with LLM reasoning
        if ctx and meeting_context:
            try:
                llm = LLMGateway().chat_model
                improvement_prompt = FUN_FACT_ENHANCEMENT_PROMPT.format(
                    fun_fact=fun_fact.text,
                    meeting_context=meeting_context
                )
                
                response = await llm.ainvoke([{"role": "user", "content": improvement_prompt}])
                return response.content
            except Exception as e:
                logger.warning(f"Failed to improve fun fact with LLM: {e}")
        
        # Return basic fun fact if improvement fails
        return fun_fact.text
        
    except Exception as e:
        logger.error(f"Error in fun facts agent: {e}")
        return "Unable to fetch fun fact at this time."


@tool
async def github_trending_agent(ctx=None, meeting_context: str = "") -> str:
    """
    Get GitHub trending repositories using the GitHubTrendingAgent with LLM reasoning.
    This agent can filter and prioritize trending repos based on the meeting context.
    """
    try:
        # Get basic trending repos from the agent
        agent = GitHubTrendingAgent()
        trending_repos = await agent.get_trending_repos()
        
        # If we have MCP context, improve with LLM reasoning
        if ctx and meeting_context:
            try:
                llm = LLMGateway().chat_model
                
                # Format repos for LLM processing
                repos_text = "\n".join([
                    f"• {repo['name']}: {repo['description']} ({repo['language']}, {repo['stars']} stars)"
                    for repo in trending_repos[:5]  # Limit to top 5 for context
                ])
                
                improvement_prompt = TRENDING_ENHANCEMENT_PROMPT.format(
                    trending_repos=repos_text,
                    meeting_context=meeting_context
                )
                
                response = await llm.ainvoke([{"role": "user", "content": improvement_prompt}])
                return response.content
            except Exception as e:
                logger.warning(f"Failed to improve trending repos with LLM: {e}")
        
        # Return basic trending repos if improvement fails
        from ..formatters.repository_formatter import RepositoryFormatter
        return RepositoryFormatter.format_trending_repos_for_llm(trending_repos)
        
    except Exception as e:
        logger.error(f"Error in GitHub trending agent: {e}")
        return "Unable to fetch trending repositories at this time."
