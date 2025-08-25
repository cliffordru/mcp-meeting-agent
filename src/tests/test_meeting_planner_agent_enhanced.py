"""
Tests for the Enhanced Meeting Planner Agent.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.agents.meeting_planner_agent import MeetingPlannerAgent


class TestMeetingPlannerAgent:
    """Test cases for MeetingPlannerAgent."""

    @pytest.fixture
    def agent_basic(self):
        """Create agent with basic tools."""
        return MeetingPlannerAgent(use_enhanced_tools=False)

    @pytest.fixture
    def agent_enhanced(self):
        """Create agent with enhanced tools."""
        return MeetingPlannerAgent(use_enhanced_tools=True)

    def test_agent_initialization_basic(self, agent_basic):
        """Test agent initialization with basic tools."""
        assert agent_basic.use_enhanced_tools is False
        assert len(agent_basic.tools) == 3
        # Check that basic tools are used
        tool_names = [tool.name for tool in agent_basic.tools]
        assert "get_tech_trivia" in tool_names
        assert "get_fun_fact" in tool_names
        assert "get_trending_repos" in tool_names

    def test_agent_initialization_enhanced(self, agent_enhanced):
        """Test agent initialization with enhanced tools."""
        assert agent_enhanced.use_enhanced_tools is True
        assert len(agent_enhanced.tools) == 3
        # Check that enhanced tools are used
        tool_names = [tool.name for tool in agent_enhanced.tools]
        assert "enhanced_tech_trivia_agent" in tool_names
        assert "enhanced_fun_facts_agent" in tool_names
        assert "enhanced_github_trending_agent" in tool_names

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_success_basic(self, mock_ainvoke, agent_basic):
        """Test successful meeting planning with basic tools."""
        mock_result = {"output": "Meeting notes with basic tools"}
        mock_ainvoke.return_value = mock_result

        result = await agent_basic.plan_meeting("test meeting")

        assert result == "Meeting notes with basic tools"
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_success_enhanced(self, mock_ainvoke, agent_enhanced):
        """Test successful meeting planning with enhanced tools."""
        mock_result = {"output": "Enhanced meeting notes"}
        mock_ainvoke.return_value = mock_result

        result = await agent_enhanced.plan_meeting("test meeting")

        assert result == "Enhanced meeting notes"
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_with_enhanced_override(self, mock_ainvoke, agent_basic):
        """Test meeting planning with enhanced tools override."""
        mock_result = {"output": "Enhanced meeting notes with override"}
        mock_ainvoke.return_value = mock_result

        result = await agent_basic.plan_meeting("test meeting", use_enhanced=True)

        assert result == "Enhanced meeting notes with override"
        assert agent_basic.use_enhanced_tools is True
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_timeout(self, mock_ainvoke, agent_basic):
        """Test meeting planning timeout handling."""
        mock_ainvoke.side_effect = TimeoutError("Agent timeout")

        result = await agent_basic.plan_meeting("test meeting")

        # Should return fallback meeting notes
        assert "Meeting Notes" in result
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke')
    async def test_plan_meeting_exception(self, mock_ainvoke, agent_basic):
        """Test meeting planning exception handling."""
        mock_ainvoke.side_effect = Exception("Agent error")

        result = await agent_basic.plan_meeting("test meeting")

        # Should return fallback meeting notes
        assert "Meeting Notes" in result
        mock_ainvoke.assert_called_once()

    @patch('app.agents.meeting_planner_agent.asyncio.gather')
    async def test_fallback_plan_meeting_timeout(self, mock_gather, agent_basic):
        """Test fallback meeting planning timeout."""
        mock_gather.side_effect = TimeoutError("Fallback timeout")

        result = await agent_basic._fallback_plan_meeting()

        assert "Unable to prepare meeting information due to timeout" in result

    @patch('app.agents.meeting_planner_agent.asyncio.gather')
    async def test_fallback_plan_meeting_exception(self, mock_gather, agent_basic):
        """Test fallback meeting planning exception."""
        mock_gather.side_effect = Exception("Fallback error")

        result = await agent_basic._fallback_plan_meeting()

        assert "Unable to prepare meeting information at this time" in result
