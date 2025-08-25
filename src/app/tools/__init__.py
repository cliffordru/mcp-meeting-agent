"""
Tools package for LangChain tool definitions.
"""
import functools
from typing import Callable, Any, Optional
from ..core.logging_config import get_logger

logger = get_logger(__name__)


def tool_error_handler(fallback_prompt, hardcoded_fallback: str, model: str = "gpt-4o-mini"):
    """
    Decorator to handle common error patterns in LangChain tools with LLM fallback.
    
    Args:
        fallback_prompt: The LangChain prompt template for LLM fallback
        hardcoded_fallback: Hardcoded fallback string if LLM fails
        model: The LLM model to use for fallback generation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}", error=str(e))
                
                # Extract ctx from kwargs if present
                ctx = kwargs.get('ctx')
                
                # If we have MCP context, use LLM to generate contextual fallback
                if ctx:
                    try:
                        # Use MCP context to sample from LLM for dynamic fallback
                        response = await ctx.sample(
                            model=model,
                            messages=fallback_prompt.format_messages(),
                            max_tokens=200
                        )
                        return response.content
                    except Exception as llm_error:
                        logger.error(f"Error generating LLM fallback for {func.__name__}", error=str(llm_error))
                
                # Fallback to hardcoded content if LLM generation fails
                return hardcoded_fallback
        
        return wrapper
    return decorator
