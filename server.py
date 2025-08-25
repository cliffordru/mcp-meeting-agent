# server.py
import asyncio
from fastmcp import FastMCP
from src.app.agents.meeting_planner_agent import MeetingPlannerAgent
from src.app.core.config import settings
from src.app.core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

mcp = FastMCP(
    name="Meeting Preparation Agent",
    instructions="A meeting preparation agent that prepares interesting meeting notes for the user.",
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
async def prepare_meeting() -> str:
    """Prepares a meeting for the user."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        logger.info(
            "Meeting preparation requested",
            timeout_seconds=settings.MCP_TOOL_TIMEOUT
        )
        
        # Add timeout to the entire tool execution
        result = await asyncio.wait_for(
            planner_agent.plan_meeting(),
            timeout=settings.MCP_TOOL_TIMEOUT
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.info(
            "Meeting preparation completed successfully",
            execution_time_seconds=round(execution_time, 2)
        )
        return result
        
    except asyncio.TimeoutError:
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.error(
            "Meeting preparation timed out",
            timeout_seconds=settings.MCP_TOOL_TIMEOUT,
            execution_time_seconds=round(execution_time, 2)
        )
        return "Meeting preparation timed out. Please try again."
        
    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        logger.error(
            "Error in meeting preparation", 
            error=str(e),
            execution_time_seconds=round(execution_time, 2)
        )
        return f"Error preparing meeting: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting MCP server", 
                host=settings.MCP_HOST, 
                port=settings.MCP_PORT, 
                transport=settings.MCP_TRANSPORT)
    mcp.run(transport=settings.MCP_TRANSPORT, host=settings.MCP_HOST, port=settings.MCP_PORT)