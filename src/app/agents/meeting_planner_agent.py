"""
Enhanced LangChain-based meeting planner agent that can use both basic tools and agent tools.
This agent provides intelligent orchestration with context-aware enhancement capabilities.
"""
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent

from ..tools.meeting_tools import get_tech_trivia, get_fun_fact, get_trending_repos
from ..tools.agent_tools import enhanced_tech_trivia_agent, enhanced_fun_facts_agent, enhanced_github_trending_agent
from ..core.llm_gateway import LLMGateway
from ..core.logging_config import get_logger
from ..core.config import settings
from ..formatters.meeting_notes_formatter import MeetingNotesFormatter
from ..prompts.agent_prompts import MEETING_PLANNER_PROMPT

logger = get_logger(__name__)


class MeetingPlannerAgent:
    """
    Enhanced LangChain-based agent for planning meetings using both basic tools and agent tools.
    This agent can choose between basic tools (fast, reliable) and enhanced agent tools (intelligent, contextual).
    """
    
    def __init__(self, use_enhanced_tools: bool = True):
        self.llm_gateway = LLMGateway()
        self.use_enhanced_tools = use_enhanced_tools
        
        # Choose tools based on configuration
        if use_enhanced_tools:
            self.tools = [
                enhanced_tech_trivia_agent,
                enhanced_fun_facts_agent, 
                enhanced_github_trending_agent
            ]
            logger.info("Using enhanced agent tools for intelligent meeting preparation")
        else:
            self.tools = [get_tech_trivia, get_fun_fact, get_trending_repos]
            logger.info("Using basic tools for reliable meeting preparation")
        
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
    
    def _log_execution_time(self, start_time: float, success: bool, **kwargs):
        """Log execution time with consistent formatting."""
        execution_time = asyncio.get_event_loop().time() - start_time
        execution_time_rounded = round(execution_time, 2)
        
        if success:
            logger.info(
                "Successfully completed operation",
                execution_time_seconds=execution_time_rounded,
                **kwargs
            )
        else:
            logger.error(
                "Operation failed",
                execution_time_seconds=execution_time_rounded,
                **kwargs
            )
        
        return execution_time_rounded
    
    async def plan_meeting(self, meeting_context: str = "", use_enhanced: bool = None) -> str:
        """
        Plan a meeting using the LangChain agent framework.
        
        Args:
            meeting_context: Context about the meeting (type, audience, etc.)
            use_enhanced: Override the default enhanced tools setting
        """
        start_time = asyncio.get_event_loop().time()
        
        # Override enhanced tools setting if specified
        if use_enhanced is not None:
            self.use_enhanced_tools = use_enhanced
        
        try:
            logger.info(
                "Starting enhanced LangChain-based meeting planning", 
                context=meeting_context,
                enhanced_tools=self.use_enhanced_tools,
                timeout_seconds=settings.AGENT_EXECUTOR_TIMEOUT
            )
            
            # Prepare input with context for enhanced tools
            if self.use_enhanced_tools and meeting_context:
                input_text = f"Prepare enhanced meeting notes for: {meeting_context}. Use the enhanced tools to make content more relevant and engaging."
            else:
                input_text = f"Prepare meeting notes for: {meeting_context or 'a general tech meeting'}"
            
            # Add timeout to the agent execution
            result = await asyncio.wait_for(
                self.agent_executor.ainvoke({
                    "input": input_text,
                    "chat_history": []
                }),
                timeout=settings.AGENT_EXECUTOR_TIMEOUT
            )
            
            self._log_execution_time(start_time, True, enhanced_tools=self.use_enhanced_tools)
            return result["output"]
            
        except asyncio.TimeoutError:
            self._log_execution_time(
                start_time, False,
                timeout_seconds=settings.AGENT_EXECUTOR_TIMEOUT,
                context=meeting_context,
                enhanced_tools=self.use_enhanced_tools
            )
            return await self._fallback_plan_meeting()
            
        except Exception as e:
            self._log_execution_time(
                start_time, False,
                error=str(e),
                context=meeting_context,
                enhanced_tools=self.use_enhanced_tools
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
            
            self._log_execution_time(start_time, True)
            return result
            
        except asyncio.TimeoutError:
            self._log_execution_time(start_time, False)
            return "Unable to prepare meeting information due to timeout."
            
        except Exception as e:
            self._log_execution_time(start_time, False, error=str(e))
            return "Unable to prepare meeting information at this time."
