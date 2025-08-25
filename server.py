# server.py
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
    logger.info("Meeting preparation requested")
    try:
        result = await planner_agent.plan_meeting()
        logger.info("Meeting preparation completed successfully")
        return result
    except Exception as e:
        logger.error("Error in meeting preparation", error=str(e))
        return f"Error preparing meeting: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting MCP server", 
                host=settings.MCP_HOST, 
                port=settings.MCP_PORT, 
                transport=settings.MCP_TRANSPORT)
    mcp.run(transport=settings.MCP_TRANSPORT, host=settings.MCP_HOST, port=settings.MCP_PORT)