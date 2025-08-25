"""
Handles application configuration using Pydantic Settings.

This module defines the `Settings` class, which loads configuration values
from environment variables and a .env file.
"""
from typing import Optional
from pydantic import SecretStr, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Defines the application's configuration settings.
    
    Pydantic automatically reads these settings from environment variables
    or a .env file.
    """
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # API Configuration
    TECH_TRIVIA_API_URL: str = "https://opentdb.com/api.php?amount=1&category=18&type=multiple"
    FUN_FACTS_API_URL: str = "https://uselessfacts.jsph.pl/random.json?language=en"
    GITHUB_TRENDING_URL: str = "https://api.ossinsight.io/v1/trends/repos/"

    # Timeout Configuration (in seconds)
    API_TIMEOUT: int = 30  # Increased from 10 to 30 seconds for rate-limited APIs
    LLM_REQUEST_TIMEOUT: int = 60  # Increased from 15 to 60 seconds for complex agent operations
    AGENT_EXECUTOR_TIMEOUT: int = 120  # New: 2 minutes for agent execution
    MCP_TOOL_TIMEOUT: int = 150  # New: 2.5 minutes for MCP tool execution

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # Server Configuration
    MCP_HOST: str = "127.0.0.1"
    MCP_PORT: int = 8000
    MCP_TRANSPORT: str = "sse"

    # LLM Configuration (for future use)
    LLM_API_KEY: Optional[SecretStr] = None
    LLM_API_BASE_URL: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    LLM_TEMPERATURE: float = 0.0  # Use 0 for deterministic, structured output

    # Optional Langfuse settings
    LANGFUSE_SECRET_KEY: Optional[SecretStr] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None

    # FastMCP Configuration
    MCP_MASK_ERROR_DETAILS: bool = True  # Hide internal errors from clients
    MCP_ENABLE_LOGGING: bool = True      # Enable MCP client logging

settings = Settings()
