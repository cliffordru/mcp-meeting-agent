# server.py
import asyncio
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from src.app.agents.meeting_planner_agent import MeetingPlannerAgent
from src.app.core.config import settings
from src.app.core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Production-ready FastMCP configuration
mcp = FastMCP(
    name="Meeting Preparation Agent",
    instructions="A meeting preparation agent that prepares interesting meeting notes for the user.",
    mask_error_details=settings.MCP_MASK_ERROR_DETAILS,  # Configurable error masking
)

# Initialize the LangChain-based planner agent
planner_agent = MeetingPlannerAgent()
logger.info("MCP server initialized with LangChain-based planner agent")

@mcp.prompt
def prepare_meeting_prompt() -> str:
    """Creates a prompt asking for meeting info."""
    logger.info("Meeting prompt requested")
    return "Please prepare a meeting for the user."

@mcp.tool
async def prepare_meeting(ctx: Context, meeting_context: str = "") -> str:
    """Prepares a meeting for the user with enhanced error handling and context."""
    start_time = asyncio.get_event_loop().time()
    
    # Log to MCP client for better debugging
    ctx.info(f"Starting meeting preparation for: {meeting_context or 'general meeting'}")
    
    try:
        logger.info(
            "Meeting preparation requested",
            timeout_seconds=settings.MCP_TOOL_TIMEOUT,
            context=meeting_context
        )
        
        # Add timeout to the entire tool execution
        result = await asyncio.wait_for(
            planner_agent.plan_meeting(meeting_context),
            timeout=settings.MCP_TOOL_TIMEOUT
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Log success to both server and MCP client
        logger.info(
            "Meeting preparation completed successfully",
            execution_time_seconds=round(execution_time, 2)
        )
        ctx.info(f"Meeting preparation completed in {round(execution_time, 2)}s")
        
        return result
        
    except asyncio.TimeoutError:
        execution_time = asyncio.get_event_loop().time() - start_time
        error_msg = "Meeting preparation timed out. Please try again."
        
        logger.error(
            "Meeting preparation timed out",
            timeout_seconds=settings.MCP_TOOL_TIMEOUT,
            execution_time_seconds=round(execution_time, 2),
            context=meeting_context
        )
        ctx.error(f"Meeting preparation timed out after {round(execution_time, 2)}s")
        
        # Use ToolError for client-visible timeout errors
        raise ToolError(error_msg)
        
    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Log detailed error internally
        logger.error(
            "Error in meeting preparation", 
            error=str(e),
            execution_time_seconds=round(execution_time, 2),
            context=meeting_context
        )
        
        # Log generic error to MCP client
        ctx.error(f"Meeting preparation failed after {round(execution_time, 2)}s")
        
        # Use ToolError for client-visible errors, masking internal details
        raise ToolError("Unable to prepare meeting at this time. Please try again later.")

if __name__ == "__main__":
    logger.info("Starting MCP server", 
                host=settings.MCP_HOST, 
                port=settings.MCP_PORT, 
                transport=settings.MCP_TRANSPORT)
    mcp.run(transport=settings.MCP_TRANSPORT, host=settings.MCP_HOST, port=settings.MCP_PORT)