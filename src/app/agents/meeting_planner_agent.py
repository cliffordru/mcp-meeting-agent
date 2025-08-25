"""
LangChain-based meeting planner agent that coordinates tools for meeting preparation.
"""
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage

from ..tools.meeting_tools import get_tech_trivia, get_fun_fact, get_trending_repos
from ..core.llm_gateway import LLMGateway
from ..core.logging_config import get_logger
from ..core.config import settings
from ..formatters.meeting_notes_formatter import MeetingNotesFormatter
from ..prompts.agent_prompts import MEETING_PLANNER_PROMPT

logger = get_logger(__name__)


class MeetingPlannerAgent:
    """LangChain-based agent for planning meetings using tools."""
    
    def __init__(self):
        self.llm_gateway = LLMGateway()
        self.tools = [get_tech_trivia, get_fun_fact, get_trending_repos]
        
        # Create the agent using centralized prompt - provider agnostic
        self.agent = create_tool_calling_agent(
            llm=self.llm_gateway.chat_model,
            tools=self.tools,
            prompt=MEETING_PLANNER_PROMPT
        )
        
        # Create the executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    async def plan_meeting(self, meeting_context: str = "") -> str:
        """Plan a meeting using the LangChain agent framework."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(
                "Starting LangChain-based meeting planning", 
                context=meeting_context,
                timeout_seconds=settings.AGENT_EXECUTOR_TIMEOUT
            )
            
            # Add timeout to the agent execution
            result = await asyncio.wait_for(
                self.agent_executor.ainvoke({
                    "input": f"Prepare meeting notes for: {meeting_context or 'a general tech meeting'}",
                    "chat_history": []
                }),
                timeout=settings.AGENT_EXECUTOR_TIMEOUT
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.info(
                "Successfully completed meeting planning with LangChain agent",
                execution_time_seconds=round(execution_time, 2)
            )
            return result["output"]
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                "LangChain agent execution timed out",
                timeout_seconds=settings.AGENT_EXECUTOR_TIMEOUT,
                execution_time_seconds=round(execution_time, 2),
                context=meeting_context
            )
            return await self._fallback_plan_meeting()
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                "Error in LangChain meeting planning", 
                error=str(e),
                execution_time_seconds=round(execution_time, 2),
                context=meeting_context
            )
            return await self._fallback_plan_meeting()
    
    async def _fallback_plan_meeting(self) -> str:
        """Fallback method that uses the original formatter if LangChain agent fails."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Using fallback meeting planning method")
            
            # Call tools directly for fallback with individual timeouts
            from ..services.tech_trivia_service import TechTriviaService
            from ..services.fun_facts_service import FunFactsService
            from ..services.github_trending_service import GitHubTrendingService
            
            # Get data from services with timeouts
            tech_trivia_service = TechTriviaService()
            fun_facts_service = FunFactsService()
            github_trending_service = GitHubTrendingService()
            
            # Execute services with timeouts
            trivia_task = asyncio.create_task(tech_trivia_service.get_tech_trivia())
            fun_fact_task = asyncio.create_task(fun_facts_service.get_fun_fact())
            trending_repos_task = asyncio.create_task(github_trending_service.get_trending_repos())
            
            # Wait for all tasks with timeout
            tasks = [trivia_task, fun_fact_task, trending_repos_task]
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=settings.API_TIMEOUT * 2  # Double the API timeout for multiple calls
            )
            
            # Extract results, handling any exceptions
            trivia_question = results[0] if not isinstance(results[0], Exception) else "Unable to fetch trivia"
            fun_fact = results[1] if not isinstance(results[1], Exception) else "Unable to fetch fun fact"
            trending_repos = results[2] if not isinstance(results[2], Exception) else "Unable to fetch trending repos"
            
            # Use the existing formatter
            result = MeetingNotesFormatter.format_meeting_notes(
                trivia_question, fun_fact, trending_repos
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.info(
                "Successfully completed fallback meeting planning",
                execution_time_seconds=round(execution_time, 2)
            )
            return result
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                "Fallback meeting planning timed out",
                execution_time_seconds=round(execution_time, 2)
            )
            return "Unable to prepare meeting information due to timeout."
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(
                "Error in fallback meeting planning", 
                error=str(e),
                execution_time_seconds=round(execution_time, 2)
            )
            return "Unable to prepare meeting information at this time."
