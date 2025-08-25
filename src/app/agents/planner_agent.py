import asyncio
from .tech_trivia_agent import TechTriviaAgent
from .fun_facts_agent import FunFactsAgent
from .github_trending_agent import GitHubTrendingAgent
from ..core.llm_gateway import LLMGateway
from ..core.logging_config import get_logger
from ..formatters.meeting_notes_formatter import MeetingNotesFormatter

logger = get_logger(__name__)

class PlannerAgent:
    def __init__(self):
        self.llm_gateway = LLMGateway()
        logger.info("PlannerAgent initialized with LLM gateway")
    
    async def plan_meeting_async(self) -> str:
        """Async version of plan_meeting that uses the LLM gateway."""
        try:
            logger.info("Starting meeting planning process")
            
            # Call the tech trivia agent to get a trivia question
            tech_trivia_agent = TechTriviaAgent()
            trivia_question = await tech_trivia_agent.get_tech_trivia()
            logger.info("Retrieved tech trivia", trivia_question=trivia_question.question)

            # Call the fun facts agent to get a fun fact
            fun_facts_agent = FunFactsAgent()
            fun_fact = await fun_facts_agent.get_fun_fact()
            logger.info("Retrieved fun fact", fun_fact_length=len(fun_fact.text))
            
            # Call the GitHub trending agent to get trending repositories
            github_trending_agent = GitHubTrendingAgent()
            trending_repos = await github_trending_agent.get_trending_repos()
            logger.info("Retrieved GitHub trending repos", trending_count=len(trending_repos))
            
            # Use the LLM gateway to format the structured outputs
            formatted_info = await self.llm_gateway.format_meeting_info(
                trivia_question, fun_fact, trending_repos
            )
            
            logger.info("Successfully formatted meeting info", 
                       trivia_question_length=len(formatted_info.trivia_question),
                       trending_repos_count=len(formatted_info.trending_repos))
            
            # Return the nicely formatted result
            return formatted_info.summary
            
        except Exception as e:
            logger.error("Error in meeting planning process", error=str(e))
            # Fallback to simple concatenation if LLM fails
            return await self._fallback_plan_meeting()
    
    async def _fallback_plan_meeting(self) -> str:
        """Fallback method that combines structured outputs without LLM processing."""
        try:
            # Call the tech trivia agent to get a trivia question
            tech_trivia_agent = TechTriviaAgent()
            trivia_question = await tech_trivia_agent.get_tech_trivia()

            # Call the fun facts agent to get a fun fact
            fun_facts_agent = FunFactsAgent()
            fun_fact = await fun_facts_agent.get_fun_fact()
            
            # Call the GitHub trending agent to get trending repositories
            github_trending_agent = GitHubTrendingAgent()
            trending_repos = await github_trending_agent.get_trending_repos()
            
            # Use the MeetingNotesFormatter to format the meeting notes
            return MeetingNotesFormatter.format_meeting_notes(trivia_question, fun_fact, trending_repos)
            
        except Exception as e:
            logger.error("Error in fallback meeting planning", error=str(e))
            return "Unable to prepare meeting information at this time."