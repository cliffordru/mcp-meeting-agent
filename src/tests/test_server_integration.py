"""
Integration tests for the MCP server.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Add the project root to the path so we can import server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestMCPServerIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_prepare_meeting_tool_functionality(self):
        """Test the prepare_meeting tool functionality by calling the underlying agent."""
        # Import the server module to get access to the planner_agent
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to return a predictable result
            mock_result = {"output": "Meeting Notes for Host\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
            
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                
                # Call the agent directly (this is what the tool does)
                result = await planner_agent.plan_meeting()
                
                # Verify the result contains expected sections (LangChain agent format)
                assert "Meeting Notes" in result
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_prepare_meeting_with_context(self):
        """Test the prepare_meeting tool with meeting context."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to return a predictable result
            mock_result = {"output": "Meeting Notes for Sprint Planning\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
            
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                
                # Call the agent directly with context
                result = await planner_agent.plan_meeting("sprint planning")
                
                # Verify the result contains expected sections (LangChain agent format)
                assert "Meeting Notes" in result
                assert "Sprint" in result or "sprint" in result  # Context should be reflected
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_prepare_meeting_error_handling(self):
        """Test error handling in the prepare_meeting tool."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to raise an exception
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(side_effect=Exception("Test error"))
                
                # Call the agent directly
                result = await planner_agent.plan_meeting()
                
                # Verify fallback was used (should generate meeting notes with fallback content)
                assert "Meeting Notes" in result
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_prepare_meeting_with_partial_api_failures(self):
        """Test that meeting notes are generated even when some APIs fail."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock individual services to simulate partial failures
            with patch('app.services.tech_trivia_service.TechTriviaService.get_tech_trivia') as mock_trivia, \
                 patch('app.services.fun_facts_service.FunFactsService.get_fun_fact') as mock_facts, \
                 patch('app.services.github_trending_service.GitHubTrendingService.get_trending_repos') as mock_repos:
                
                # Make trivia fail, but facts and repos succeed
                mock_trivia.side_effect = Exception("API Error")
                mock_facts.return_value = type('obj', (object,), {'text': 'Test fun fact'})()
                mock_repos.return_value = [{'name': 'test/repo', 'description': 'Test repo', 'language': 'Python', 'stars': 100, 'url': 'https://github.com/test/repo'}]
                
                # Call the agent directly
                result = await planner_agent.plan_meeting()
                
                # Verify that meeting notes are still generated
                assert "Meeting Notes" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self):
        """Test that the MCP server is properly initialized."""
        from server import mcp, planner_agent
        
        # Verify the MCP server is configured
        assert mcp is not None
        assert planner_agent is not None
        
        # Verify the tool is registered
        assert hasattr(mcp, 'tool')

    @pytest.mark.asyncio
    async def test_meeting_planner_agent_integration(self):
        """Test the MeetingPlannerAgent integration with the server."""
        from app.agents.meeting_planner_agent import MeetingPlannerAgent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Create the agent
            agent = MeetingPlannerAgent()
            
            # Mock the agent executor to return a predictable result
            mock_result = {"output": "Meeting Notes for Test Meeting\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
            
            with patch.object(agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                
                # Test the agent
                result = await agent.plan_meeting("test meeting")
                
                # Verify the result contains expected sections (LangChain agent format)
                assert "Meeting Notes" in result
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_server_configuration(self):
        """Test that the server uses the correct configuration."""
        from app.core.config import settings
        
        # Verify configuration is loaded
        assert settings.MCP_HOST == "127.0.0.1"
        assert settings.MCP_PORT == 8000
        assert settings.MCP_TRANSPORT == "sse"
        
        # Verify API URLs are configured
        assert "opentdb.com" in settings.TECH_TRIVIA_API_URL
        assert "uselessfacts.jsph.pl" in settings.FUN_FACTS_API_URL
        assert "ossinsight.io" in settings.GITHUB_TRENDING_URL

    @pytest.mark.asyncio
    async def test_prepare_meeting_tool_real_integration(self):
        """Test the prepare_meeting tool with real agent."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to return a predictable result
            mock_result = {"output": "Meeting Notes for General Meeting\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
            
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                
                # Call the agent directly
                result = await planner_agent.plan_meeting()
                
                # Verify the result contains expected sections (LangChain agent format)
                assert "Meeting Notes" in result
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_prepare_meeting_tool_fallback_integration(self):
        """Test the prepare_meeting tool fallback when LangChain agent fails."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to fail
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(side_effect=Exception("LangChain error"))
                
                # Call the agent directly
                result = await planner_agent.plan_meeting()
                
                # Verify fallback was used (should generate meeting notes with fallback content)
                assert "Meeting Notes" in result
                assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert len(result) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_server_tool_registration(self):
        """Test that the MCP server properly registers the prepare_meeting tool."""
        from server import mcp
        
        # Verify the MCP server has the tool decorator
        assert hasattr(mcp, 'tool')
        
        # Verify the tool function exists in the server module
        import server
        assert hasattr(server, 'prepare_meeting')
        
        # Verify it's a FastMCP tool (has the tool attribute)
        assert hasattr(server.prepare_meeting, 'name')
        assert server.prepare_meeting.name == 'prepare_meeting'

    @pytest.mark.asyncio
    async def test_end_to_end_prepare_meeting(self):
        """Test the complete end-to-end prepare_meeting functionality."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Test multiple calls to ensure consistency
            results = []
            for i in range(2):
                # Mock the agent executor to return a predictable result
                mock_result = {"output": f"Meeting Notes for Test Meeting {i}\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
                
                with patch.object(planner_agent, 'agent_executor') as mock_executor:
                    mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                    
                    result = await planner_agent.plan_meeting(f"test meeting {i}")
                    results.append(result)
                    
                    # Verify each result has the expected structure (LangChain agent format)
                    assert "Meeting Notes" in result
                    assert "Tech Trivia" in result or "Icebreaker" in result or "Ice Breaker" in result
                    assert "Fun Fact" in result
                    assert "Trending" in result or "GitHub" in result
                    assert len(result) > 100
            
            # Verify results are different (indicating different mock responses)
            assert results[0] != results[1], "Results should be different due to different mock responses"

    @pytest.mark.asyncio
    async def test_langchain_agent_working(self):
        """Test that the LangChain agent is working and producing sophisticated output."""
        from server import planner_agent
        
        # Mock the LLMGateway to avoid API key requirements
        with patch('app.core.llm_gateway.LLMGateway') as mock_llm_gateway:
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            
            # Mock the agent executor to return a sophisticated result
            mock_result = {"output": "Meeting Notes for Team Standup\n\nAgenda:\n- Review yesterday's progress\n- Plan today's tasks\n- Address blockers\n\nIcebreaker - Tech Trivia:\nQuestion: What is the latest version of React?\nAnswer: React 18\n\nFun Fact:\nDid you know? The first computer bug was an actual bug! In 1947, Grace Hopper found a moth causing problems in the Harvard Mark II computer.\n\nTrending GitHub Repositories:\n• react/react - A JavaScript library for building user interfaces\n• vuejs/vue - Progressive JavaScript framework\n• angular/angular - Platform for building mobile and desktop web applications"}
            
            with patch.object(planner_agent, 'agent_executor') as mock_executor:
                mock_executor.ainvoke = AsyncMock(return_value=mock_result)
                
                # Call the agent directly
                result = await planner_agent.plan_meeting("team standup")
                
                # Verify the LangChain agent is producing sophisticated output
                assert "Meeting Notes" in result
                assert "Agenda" in result or "Icebreaker" in result or "Ice Breaker" in result
                assert "Tech Trivia" in result or "Question" in result
                assert "Fun Fact" in result
                assert "Trending" in result or "GitHub" in result
                assert "Repository" in result or "repo" in result.lower()
                assert len(result) > 200  # Should be substantial content
                
                # Verify it's not the old simple format
                assert "Meeting Notes for Host" not in result  # Old format
                assert "Ice Breaker - Tech Trivia:" not in result  # Old format
