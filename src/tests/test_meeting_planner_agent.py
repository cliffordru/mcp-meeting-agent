"""
Tests for the LangChain-based MeetingPlannerAgent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.meeting_planner_agent import MeetingPlannerAgent
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact


class TestMeetingPlannerAgent:
    """Test cases for MeetingPlannerAgent."""

    @pytest.fixture
    def agent(self):
        """Create a MeetingPlannerAgent instance for testing."""
        with patch('app.agents.meeting_planner_agent.LLMGateway') as mock_llm_gateway:
            # Mock the LLMGateway to avoid API key requirements
            mock_gateway_instance = MagicMock()
            mock_llm_gateway.return_value = mock_gateway_instance
            return MeetingPlannerAgent()

    @pytest.mark.asyncio
    async def test_plan_meeting_success(self, agent):
        """Test successful meeting planning with LangChain agent."""
        mock_result = {"output": "Meeting Notes for Host\n\nTech Trivia: What is Python?\nAnswer: A programming language\n\nFun Fact: The average person spends 6 months waiting for red lights.\n\nTrending Repositories:\n- repo1: Test repo 1 (Python, 1000 stars)\n- repo2: Test repo 2 (JavaScript, 500 stars)"}
        
        with patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_result
            
            result = await agent.plan_meeting("team standup")
            
            assert "Meeting Notes for Host" in result
            assert "Tech Trivia" in result
            assert "Fun Fact" in result
            assert "Trending Repositories" in result
            mock_ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_plan_meeting_langchain_failure_fallback(self, agent):
        """Test fallback to original formatter when LangChain agent fails."""
        with patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.side_effect = Exception("LangChain error")
            
            # Mock the fallback services
            with patch('app.services.tech_trivia_service.TechTriviaService') as mock_trivia_service_class, \
                 patch('app.services.fun_facts_service.FunFactsService') as mock_facts_service_class, \
                 patch('app.services.github_trending_service.GitHubTrendingService') as mock_github_service_class, \
                 patch.object(MeetingPlannerAgent, '_fallback_plan_meeting') as mock_fallback:
                
                # Setup service mocks with proper return values
                mock_trivia_service = AsyncMock()
                mock_facts_service = AsyncMock()
                mock_github_service = AsyncMock()
                
                # Create proper data objects
                mock_trivia = TechTriviaQuestion(
                    category="Science: Computers",
                    type="multiple",
                    difficulty="easy",
                    question="What is Python?",
                    correct_answer="A programming language",
                    incorrect_answers=["A snake", "A game", "A database"]
                )
                
                mock_fact = FunFact(
                    id="123",
                    text="The average person spends 6 months waiting for red lights.",
                    source="Useless Facts API",
                    source_url="https://uselessfacts.jsph.pl/",
                    language="en",
                    permalink="https://uselessfacts.jsph.pl/fact/123"
                )
                
                mock_repos = [
                    {"name": "repo1", "description": "Test repo 1", "language": "Python", "stars": "1000", "url": "https://github.com/repo1"}
                ]
                
                mock_trivia_service.get_tech_trivia.return_value = mock_trivia
                mock_facts_service.get_fun_fact.return_value = mock_fact
                mock_github_service.get_trending_repos.return_value = mock_repos
                
                mock_trivia_service_class.return_value = mock_trivia_service
                mock_facts_service_class.return_value = mock_facts_service
                mock_github_service_class.return_value = mock_github_service
                
                # Setup fallback mock
                mock_fallback.return_value = "Fallback meeting notes"
                
                result = await agent.plan_meeting("team standup")
                
                assert result == "Fallback meeting notes"
                mock_ainvoke.assert_called_once()
                mock_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_plan_meeting_fallback_failure(self, agent):
        """Test when both LangChain agent and fallback fail."""
        with patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.side_effect = Exception("LangChain error")
            
            # Mock the fallback services to also fail
            with patch('app.services.tech_trivia_service.TechTriviaService') as mock_trivia_service_class:
                mock_trivia_service = AsyncMock()
                mock_trivia_service.get_tech_trivia.side_effect = Exception("Service error")
                mock_trivia_service_class.return_value = mock_trivia_service
                
                result = await agent.plan_meeting("team standup")
                
                assert "Unable to prepare meeting information" in result

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test that the agent is properly initialized with tools and LLM."""
        assert agent.llm_gateway is not None
        assert len(agent.tools) == 3
        assert agent.agent is not None
        assert agent.agent_executor is not None

    @pytest.mark.asyncio
    async def test_plan_meeting_empty_context(self, agent):
        """Test meeting planning with empty context."""
        mock_result = {"output": "Meeting Notes for Host\n\nGeneral meeting content"}
        
        with patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_result
            
            result = await agent.plan_meeting("")
            
            assert "Meeting Notes for Host" in result
            # Verify the input includes the default context
            call_args = mock_ainvoke.call_args[0][0]
            assert "general tech meeting" in call_args["input"]

    @pytest.mark.asyncio
    async def test_plan_meeting_with_context(self, agent):
        """Test meeting planning with specific context."""
        mock_result = {"output": "Meeting Notes for Host\n\nSprint planning content"}
        
        with patch('app.agents.meeting_planner_agent.AgentExecutor.ainvoke', new_callable=AsyncMock) as mock_ainvoke:
            mock_ainvoke.return_value = mock_result
            
            result = await agent.plan_meeting("sprint planning")
            
            assert "Meeting Notes for Host" in result
            # Verify the input includes the specific context
            call_args = mock_ainvoke.call_args[0][0]
            assert "sprint planning" in call_args["input"]
