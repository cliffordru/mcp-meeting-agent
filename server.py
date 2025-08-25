"""
MCP Server for Meeting Preparation Agent.
"""
import asyncio
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

from src.app.agents.meeting_planner_agent import MeetingPlannerAgent
from src.app.core.config import settings
from src.app.core.logging_config import setup_logging, get_logger

# Initialize logging first
setup_logging()

logger = get_logger(__name__)

# Initialize the meeting planner agent
planner_agent = MeetingPlannerAgent()

# Initialize FastMCP server
mcp = FastMCP(
    "Meeting Preparation Agent",
    mask_error_details=settings.MCP_MASK_ERROR_DETAILS
)

logger.info("MCP server initialized with LangChain-based planner agent")


@mcp.tool
async def prepare_meeting(ctx: Context, meeting_context: str = "") -> str:
    """
    Prepare comprehensive meeting notes with trivia, fun facts, and trending repositories.
    
    Args:
        ctx: MCP context for logging and LLM sampling
        meeting_context: Description of the meeting (type, audience, topic, etc.)
    
    Returns:
        Formatted meeting notes ready for the host
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        ctx.info(f"Starting meeting preparation for: {meeting_context or 'general meeting'}")
        
        # Add timeout to the tool execution
        result = await asyncio.wait_for(
            planner_agent.plan_meeting(meeting_context),
            timeout=settings.MCP_TOOL_TIMEOUT
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            "Successfully prepared meeting notes",
            execution_time_seconds=round(execution_time, 2),
            context=meeting_context
        )
        
        return result
        
    except asyncio.TimeoutError:
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.error(
            "Meeting preparation timed out",
            execution_time_seconds=round(execution_time, 2),
            timeout_seconds=settings.MCP_TOOL_TIMEOUT,
            context=meeting_context
        )
        ctx.error("Meeting preparation timed out")
        raise ToolError("Meeting preparation timed out. Please try again.")
        
    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.error(
            "Error in meeting preparation",
            execution_time_seconds=round(execution_time, 2),
            error=str(e),
            context=meeting_context
        )
        ctx.error("Failed to prepare meeting notes")
        raise ToolError("Unable to prepare meeting notes at this time.")


if __name__ == "__main__":
    logger.info("Starting MCP server", host=settings.MCP_HOST, port=settings.MCP_PORT, transport=settings.MCP_TRANSPORT)
    
    # Run the MCP server
    mcp.run(
        transport=settings.MCP_TRANSPORT,
        host=settings.MCP_HOST,
        port=settings.MCP_PORT,
        log_level=settings.MCP_LOG_LEVEL if hasattr(settings, 'MCP_LOG_LEVEL') else "INFO"
    )