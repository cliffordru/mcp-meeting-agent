# MCP Meeting Agent

A meeting preparation agent that provides trivia, fun facts, and GitHub trending repositories to enhance your meetings.

## Proof of Concept

**This is a proof of concept application and is not intended for production use.** This project demonstrates architectural patterns and integration concepts but lacks critical production features such as security, performance optimization, comprehensive testing, and scalability considerations.

## Features

- **Tech Trivia**: Fetches technology trivia questions and answers from Open Trivia Database
- **Fun Facts**: Provides interesting random facts from Useless Facts API
- **GitHub Trending**: Shows current trending repositories from OSS Insight API
- **Meeting Notes**: Generates formatted meeting notes for hosts
- **LLM Integration**: Uses Large Language Models for intelligent content formatting
- **Structured Logging**: Comprehensive logging with configurable levels
- **Comprehensive Testing**: Full test coverage for all components

## Architecture

The project follows a clean architecture with separation of concerns:

- **Agents**: High-level orchestrators that coordinate services
- **Services**: Handle external API interactions and data fetching
- **Schemas**: Pydantic models for data validation and structure
- **Formatters**: Format data for different output types (LLM, notes)
- **Prompts**: Manage LLM prompt templates
- **Core**: Configuration, logging, and LLM gateway

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

**Current State**: Basic unit tests with 82% coverage
**Production Needs**:
- **Load Testing**: Apache Bench, Artillery, or k6 for API performance testing
- **Integration Testing**: End-to-end testing with real API dependencies
- **Failure Scenario Testing**: Network failures, API rate limits, LLM timeouts
- **Evaluation Framework**: TBD
- **Monitoring**: Langfuse integration for LLM performance tracking

### Security Considerations

**Current State**: No security measures implemented
**Production Needs**:
- **Authentication**: OAuth 2.0 flow with proper session management
- **Input Validation**: Content filtering and sanitization for all inputs
- **Output Filtering**: LLM output validation to prevent prompt injection
- **SAST/DAST**: Static and dynamic application security testing
- **SCA**: Software composition analysis for dependency vulnerabilities
- **Rate Limiting**: API rate limiting and abuse prevention
- **Secrets Management**: TBD when needed

### Performance & Scalability

**Current State**: Basic async implementation
**Production Needs**:
- **Caching**: TBD based on load testing
- **Circuit Breakers**: Resilience patterns for external API failures
- **Horizontal Scaling**: Container orchestration (Kubernetes/Docker)

### AI Architecture Improvements

**Current State**: Basic LLM integration
**Production Needs**:
- **Model-as-a-Service**: Right-sized models for cost/latency/accuracy balance
- **Prompt Engineering**: Systematic prompt optimization and versioning
- **Reduce Manual Parsing**: Could test and evaluate tradeoffs on using an LLM to process all raw external API responses to reduce brittle parsing code currently in place.

### Integration & Real-World Services

**Current State**: Basic external APIs
**Production Needs**:
- **GitHub Integration**: Real-time issues, PRs, and repository health
- **CI/CD Integration**: Build status and deployment information
- **Jira/Linear**: Project management and sprint data
- **Slack/Teams**: Real-time notifications and team collaboration
- **Calendar Integration**: Meeting scheduling and participant management
- **Analytics**: Meeting effectiveness tracking and insights

### Monitoring & Alerting
**Current State**: Basic structured logging
**Production Needs**:
- **Observability & Alerting**:

## Project Structure

```
mcp-meeting-agent/
├── src/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── tech_trivia_agent.py
│   │   │   ├── fun_facts_agent.py
│   │   │   ├── github_trending_agent.py
│   │   │   └── planner_agent.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── llm_gateway.py
│   │   │   └── logging_config.py
│   │   ├── formatters/
│   │   │   ├── meeting_notes_formatter.py
│   │   │   └── repository_formatter.py
│   │   ├── prompts/
│   │   │   └── meeting_prompts.py
│   │   ├── schemas/
│   │   │   ├── fun_facts.py
│   │   │   ├── meeting_info.py
│   │   │   └── tech_trivia.py
│   │   └── services/
│   │       ├── fun_facts_service.py
│   │       ├── github_trending_service.py
│   │       └── tech_trivia_service.py
│   └── tests/
│       ├── test_fun_facts.py
│       ├── test_github_trending_agent.py
│       ├── test_github_trending_service.py
│       ├── test_llm_gateway.py
│       ├── test_meeting_notes.py
│       ├── test_meeting_prompts.py
│       ├── test_planner_agent.py
│       ├── test_repository_formatter.py
│       └── test_tech_trivia_agent.py
├── server.py
├── env.example
├── .env (not tracked in git)
├── LICENSE
└── README.md
```

## API Endpoints

The MCP server exposes a single tool:

- `prepare_meeting(meeting_info: str)`: Generates meeting preparation content including trivia, fun facts, and trending repositories

## MCP Client Configuration

To use this MCP server with your MCP host client, see `mcp-server-config.json` in the project root for the complete configuration example for cursor.

The server runs on `http://127.0.0.1:8000/sse` by default and provides the `prepare_meeting()` tool for generating meeting content.

## Dependencies

- **FastMCP**: MCP server framework
- **aiohttp**: Async HTTP client
- **pydantic**: Data validation
- **structlog**: Structured logging
- **langchain**: LLM integration
- **pytest**: Testing framework

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.