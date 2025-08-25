"""
Tests for the Meeting Planner Agent with agent tools support.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.agents.meeting_planner_agent import MeetingPlannerAgent


class TestMeetingPlannerAgent:
    """Test cases for MeetingPlannerAgent."""

    @pytest.fixture
    def agent(self):
        """Create agent with agent tools."""
        return MeetingPlannerAgent()

    def test_agent_initialization(self, agent):
        """Test agent initialization with agent tools."""
        assert len(agent.tools) == 3
        # Check that agent tools are used
        tool_names = [tool.name for tool in agent.tools]
        assert "tech_trivia_agent" in tool_names
        assert "fun_facts_agent" in tool_names
        assert "github_trending_agent" in tool_names

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_success(self, mock_ainvoke, agent):
        """Test successful meeting planning with agent tools."""
        mock_result = {"output": "Meeting notes with agent tools"}
        mock_ainvoke.return_value = mock_result

        result = await agent.plan_meeting("test meeting")

        assert result == "Meeting notes with agent tools"
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_timeout(self, mock_ainvoke, agent):
        """Test meeting planning timeout handling."""
        mock_ainvoke.side_effect = TimeoutError("Agent timeout")

        result = await agent.plan_meeting("test meeting")

        # Should return fallback meeting notes
        assert "Meeting Notes" in result
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_exception(self, mock_ainvoke, agent):
        """Test meeting planning exception handling."""
        mock_ainvoke.side_effect = Exception("Agent error")

        result = await agent.plan_meeting("test meeting")

        # Should return fallback meeting notes
        assert "Meeting Notes" in result
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.asyncio.gather')
    async def test_fallback_plan_meeting_timeout(self, mock_gather, agent):
        """Test fallback meeting planning timeout."""
        mock_gather.side_effect = TimeoutError("Fallback timeout")

        result = await agent._fallback_plan_meeting()

        assert "Unable to prepare meeting information due to timeout" in result

    @patch('app.agents.meeting_planner_agent.asyncio.gather')
    async def test_fallback_plan_meeting_exception(self, mock_gather, agent):
        """Test fallback meeting planning exception."""
        mock_gather.side_effect = Exception("Fallback error")

        result = await agent._fallback_plan_meeting()

        assert "Unable to prepare meeting information at this time" in result
