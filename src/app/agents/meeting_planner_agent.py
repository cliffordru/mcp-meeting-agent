"""
LangChain-based meeting planner agent that coordinates tools for meeting preparation.
"""
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from ..tools.meeting_tools import get_tech_trivia, get_fun_fact, get_trending_repos
from ..core.llm_gateway import LLMGateway
from ..core.logging_config import get_logger
from ..formatters.meeting_notes_formatter import MeetingNotesFormatter

logger = get_logger(__name__)


class MeetingPlannerAgent:
    """LangChain-based agent for planning meetings using tools."""
    
    def __init__(self):
        self.llm_gateway = LLMGateway()
        self.tools = [get_tech_trivia, get_fun_fact, get_trending_repos]
        
        # Create the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meeting preparation assistant. Your job is to:
1. Gather engaging content for meetings (trivia, fun facts, trending tech)
2. Format this content into professional meeting notes for the host
3. Ensure the content is relevant and engaging for a tech audience

Use the available tools to gather information, then format everything into clear meeting notes.
Focus on creating content that will help break the ice and keep participants engaged."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_tools_agent(
            llm=self.llm_gateway.chat_model,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    async def plan_meeting(self, meeting_context: str = "") -> str:
        """Plan a meeting using the LangChain agent framework."""
        try:
            logger.info("Starting LangChain-based meeting planning", context=meeting_context)
            
            result = await self.agent_executor.ainvoke({
                "input": f"Prepare meeting notes for: {meeting_context or 'a general tech meeting'}",
                "chat_history": []
            })
            
            logger.info("Successfully completed meeting planning with LangChain agent")
            return result["output"]
            
        except Exception as e:
            logger.error("Error in LangChain meeting planning", error=str(e))
            return await self._fallback_plan_meeting()
    
    async def _fallback_plan_meeting(self) -> str:
        """Fallback method that uses the original formatter if LangChain agent fails."""
        try:
            logger.info("Using fallback meeting planning method")
            
            # Call tools directly for fallback
            from ..services.tech_trivia_service import TechTriviaService
            from ..services.fun_facts_service import FunFactsService
            from ..services.github_trending_service import GitHubTrendingService
            
            # Get data from services
            tech_trivia_service = TechTriviaService()
            fun_facts_service = FunFactsService()
            github_trending_service = GitHubTrendingService()
            
            trivia_question = await tech_trivia_service.get_tech_trivia()
            fun_fact = await fun_facts_service.get_fun_fact()
            trending_repos = await github_trending_service.get_trending_repos()
            
            # Use the existing formatter
            return MeetingNotesFormatter.format_meeting_notes(
                trivia_question, fun_fact, trending_repos
            )
            
        except Exception as e:
            logger.error("Error in fallback meeting planning", error=str(e))
            return "Unable to prepare meeting information at this time."
