# MCP Meeting Agent

A meeting preparation agent that provides trivia, fun facts, and GitHub trending repositories to enhance your meetings. Built with LangChain's modern agent framework for intelligent orchestration and tool-based interactions.

## Proof of Concept

**This is a proof of concept application and is not intended for production use.** This project demonstrates architectural patterns and integration concepts but lacks critical production features such as security, performance optimization, comprehensive testing, and scalability considerations.

## Features

- **Tech Trivia**: Fetches technology trivia questions and answers from Open Trivia Database
- **Fun Facts**: Provides interesting random facts from Useless Facts API
- **GitHub Trending**: Shows current trending repositories from OSS Insight API
- **Meeting Notes**: Generates formatted meeting notes for hosts
- **LangChain Agent Framework**: Modern LLM agent architecture with tool-based orchestration
- **Intelligent Tool Coordination**: Agent automatically selects and uses appropriate tools
- **Robust Error Handling**: Graceful fallbacks and comprehensive error recovery
- **Structured Logging**: Comprehensive logging with configurable levels
- **Comprehensive Testing**: Full test coverage for all components
- **FastMCP Integration**: Production-ready MCP server with error masking, rate limiting, and context-aware logging

## Architecture

The project follows a modern LangChain agent architecture with clean separation of concerns:

- **LangChain Agents**: Intelligent orchestrators that coordinate tools using LLM reasoning
- **Tools**: Reusable LangChain tools that wrap external services and APIs
- **Services**: Handle external API interactions and data fetching
- **Schemas**: Pydantic models for data validation and structure
- **Formatters**: Format data for different output types (LLM, notes)
- **Prompts**: Manage LLM prompt templates
- **Core**: Configuration, logging, and LLM gateway

### Key Architectural Benefits

- **Tool-Based Design**: Individual tools can be reused across different agents
- **Intelligent Orchestration**: Agent uses LLM reasoning to determine which tools to use
- **Better Error Handling**: Tools have individual error handling with graceful fallbacks
- **Enhanced Flexibility**: Easy to add new tools without changing agent logic
- **Modern LLM Patterns**: Follows LangChain's recommended agent-tool architecture

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cliffordru/mcp-meeting-agent
   cd mcp-meeting-agent
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the MCP Server**:
   ```bash
   uv run server.py
   ```

5. **Configure MCP Client**:
   To use this MCP server with your MCP host client, see [`mcp-client-config.json`](mcp-client-config.json) in the project root for the complete configuration example.

   The server runs on `http://127.0.0.1:8000/sse` by default and provides the `prepare_meeting()` tool for generating meeting content.

6. **Use**:
   For example in Cursor, you can prompt your AI assistant "Using your MCP tools, prepare some fun meeting notes".

## Configuration

Key configuration options in `.env`:

```env
# LLM Configuration
LLM_API_KEY=your_api_key
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
LLM_REQUEST_TIMEOUT=15

# API Configuration
TECH_TRIVIA_API_URL=https://opentdb.com/api.php?amount=1&category=18&type=multiple
FUN_FACTS_API_URL=https://uselessfacts.jsph.pl/random.json?language=en
GITHUB_TRENDING_URL=https://api.ossinsight.io/v1/trends/repos/

# Logging
LOG_LEVEL=INFO

# FastMCP Configuration
MCP_MASK_ERROR_DETAILS=true
MCP_ENABLE_LOGGING=true
```

## Testing

Run all tests:
```bash
uv run pytest src/tests/ -v
```

Run with coverage:
```bash
uv run pytest src/tests/ --cov=src/app --cov-report=html
```

## Production Readiness Considerations

### Testing & Quality Assurance

**Current State**: Comprehensive unit tests with good coverage
**Production Needs**:
- **Load Testing**: Apache Bench, Artillery, or k6 for API performance testing
- **Integration Testing**: End-to-end testing with real API dependencies
- **Failure Scenario Testing**: Network failures, API rate limits, LLM timeouts
- **Evaluation Framework**: TBD
- **Monitoring**: Langfuse integration for LLM performance tracking

### Security Considerations

**Current State**: Basic FastMCP error masking and rate limiting implemented
**Production Needs**:
- **Authentication**: OAuth 2.0 flow with proper session management
- **Input Validation**: Content filtering and sanitization for all inputs
- **Output Filtering**: LLM output validation to prevent prompt injection
- **SAST/DAST**: Static and dynamic application security testing
- **SCA**: Software composition analysis for dependency vulnerabilities
- **Enhanced Rate Limiting**: More sophisticated rate limiting and abuse prevention
- **Secrets Management**: TBD when needed

### Performance & Scalability

**Current State**: Async implementation with LangChain agent framework
**Production Needs**:
- **Caching**: TBD based on load testing
- **Circuit Breakers**: Resilience patterns for external API failures
- **Horizontal Scaling**: Container orchestration (Kubernetes/Docker)

### AI Architecture Improvements

**Current State**: LangChain agent framework with tool-based architecture and LLM-generated fallback content for API failures
**Production Needs**:
- **Model-as-a-Service**: Right-sized models for cost/latency/accuracy balance
- **Prompt Engineering**: Systematic prompt optimization and versioning
- **Agent Optimization**: Fine-tune agent prompts and tool selection logic
- **Tool Validation**: Enhanced input/output validation for tools
- **Enhanced LLM-Generated Fallbacks**: Improve dynamic LLM-generated content when APIs fail
  - Generate contextual trivia questions based on meeting type/context
  - Create relevant fun facts tailored to the audience/industry
  - Provide trending tech topics specific to the team's domain
  - Maintain content freshness and relevance through AI generation

### Integration & Real-World Services

**Current State**: Basic external APIs with tool-based access
**Production Needs**:
- **GitHub Integration**: Real-time issues, PRs, and repository health
- **CI/CD Integration**: Build status and deployment information
- **Jira/Linear**: Project management and sprint data
- **Slack/Teams**: Real-time notifications and team collaboration
- **Calendar Integration**: Meeting scheduling and participant management
- **Analytics**: Meeting effectiveness tracking and insights

### Monitoring & Alerting
**Current State**: Basic structured logging with FastMCP client logging integration
**Production Needs**:
- **Observability & Alerting**: Enhanced monitoring for agent performance and tool usage
- **Centralized Logging**: Log aggregation and analysis
- **Performance Metrics**: Response time tracking and alerting

## Project Structure

```
mcp-meeting-agent/
├── src/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── tech_trivia_agent.py
│   │   │   ├── fun_facts_agent.py
│   │   │   ├── github_trending_agent.py
│   │   │   └── meeting_planner_agent.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── llm_gateway.py
│   │   │   └── logging_config.py
│   │   ├── formatters/
│   │   │   ├── meeting_notes_formatter.py
│   │   │   └── repository_formatter.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── agent_prompts.py
│   │   │   └── fallback_prompts.py
│   │   ├── schemas/
│   │   │   ├── fun_facts.py
│   │   │   └── tech_trivia.py
│   │   ├── services/
│   │   │   ├── fun_facts_service.py
│   │   │   ├── github_trending_service.py
│   │   │   └── tech_trivia_service.py
│   │   └── tools/
│   │       └── meeting_tools.py
│   └── tests/
│       ├── test_fun_facts.py
│       ├── test_github_trending_agent.py
│       ├── test_github_trending_service.py
│       ├── test_meeting_notes.py
│       ├── test_meeting_planner_agent.py
│       ├── test_meeting_tools.py
│       ├── test_repository_formatter.py
│       ├── test_server_integration.py
│       └── test_tech_trivia_agent.py
├── server.py
├── env.example
├── .env (not tracked in git)
├── LICENSE
└── README.md
```

## API Endpoints

The MCP server exposes a single tool:

- `prepare_meeting(ctx: Context, meeting_context: str = "")`: Generates meeting preparation content including trivia, fun facts, and trending repositories using LangChain agent orchestration with enhanced error handling and context-aware logging

## Dependencies

- **FastMCP**: MCP server framework
- **aiohttp**: Async HTTP client
- **pydantic**: Data validation
- **structlog**: Structured logging
- **langchain**: LLM integration and agent framework
- **langchain-core**: Core LangChain components
- **langchain-openai**: OpenAI integration for LangChain
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support

**Note**: Langfuse observability is included in dependencies but not yet implemented in the current version.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.