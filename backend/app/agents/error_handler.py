"""
Error Handling Utilities for Agents

This module provides error handling, retry logic, and rate limiting
for the agent system as per Work Plan V14.1, Epic 2.
"""

import time
import logging
from typing import Dict, Any, Callable, Optional
from functools import wraps
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class RateLimitError(AgentError):
    """Raised when rate limit is exceeded."""
    pass


class LLMError(AgentError):
    """Raised when LLM call fails."""
    pass


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            LLMError: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = min(
                        self.initial_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} attempts failed. Last error: {str(e)}"
                    )
        
        # All retries failed
        raise LLMError(f"Failed after {self.max_retries} attempts: {str(last_exception)}")


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        tokens_per_minute: int = 60,
        burst_size: int = 10,
    ):
        """
        Initialize rate limiter.
        
        Args:
            tokens_per_minute: Number of tokens to add per minute
            burst_size: Maximum burst size (bucket capacity)
        """
        self.tokens_per_minute = tokens_per_minute
        self.burst_size = burst_size
        self.refill_rate = tokens_per_minute / 60.0  # tokens per second
    
    def check_rate_limit(self, state: Dict[str, Any], user_id: str) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            state: Agent state
            user_id: User ID
            
        Returns:
            True if within limit, False otherwise
        """
        rate_limit_counters = state.get("rate_limit_counters", {})
        
        if user_id not in rate_limit_counters:
            # Initialize counter
            rate_limit_counters[user_id] = {
                "tokens": self.burst_size,
                "last_update": time.time(),
            }
            state["rate_limit_counters"] = rate_limit_counters
            return True
        
        counter = rate_limit_counters[user_id]
        current_time = time.time()
        time_passed = current_time - counter["last_update"]
        
        # Refill tokens
        tokens_to_add = time_passed * self.refill_rate
        counter["tokens"] = min(
            counter["tokens"] + tokens_to_add,
            self.burst_size
        )
        counter["last_update"] = current_time
        
        # Check if we have tokens
        if counter["tokens"] >= 1.0:
            counter["tokens"] -= 1.0
            return True
        else:
            return False
    
    def get_retry_after(self, state: Dict[str, Any], user_id: str) -> float:
        """
        Get seconds until next token is available.
        
        Args:
            state: Agent state
            user_id: User ID
            
        Returns:
            Seconds until next token
        """
        rate_limit_counters = state.get("rate_limit_counters", {})
        
        if user_id not in rate_limit_counters:
            return 0.0
        
        counter = rate_limit_counters[user_id]
        tokens_needed = 1.0 - counter["tokens"]
        
        if tokens_needed <= 0:
            return 0.0
        
        return tokens_needed / self.refill_rate


def handle_agent_errors(func: Callable) -> Callable:
    """
    Decorator to handle agent errors gracefully.
    
    Args:
        func: Agent process function
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return func(self, state)
        except RateLimitError as e:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded: {str(e)}")
            
            error_message = AIMessage(
                content="I apologize, but you've reached the rate limit. Please try again in a moment."
            )
            
            state["messages"] = state.get("messages", []) + [error_message]
            state["errors"] = state.get("errors", []) + [{
                "type": "rate_limit",
                "message": str(e),
                "timestamp": time.time(),
            }]
            
            return state
            
        except LLMError as e:
            # LLM call failed after retries
            logger.error(f"LLM error: {str(e)}")
            
            error_message = AIMessage(
                content="I apologize, but I'm having trouble processing your request right now. Please try again later."
            )
            
            state["messages"] = state.get("messages", []) + [error_message]
            state["errors"] = state.get("errors", []) + [{
                "type": "llm_error",
                "message": str(e),
                "timestamp": time.time(),
            }]
            
            return state
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in agent: {str(e)}", exc_info=True)
            
            error_message = AIMessage(
                content="I apologize, but an unexpected error occurred. Our team has been notified."
            )
            
            state["messages"] = state.get("messages", []) + [error_message]
            state["errors"] = state.get("errors", []) + [{
                "type": "unexpected_error",
                "message": str(e),
                "timestamp": time.time(),
            }]
            
            return state
    
    return wrapper


# Global retry handler instance
retry_handler = RetryHandler(
    max_retries=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
)

# Global rate limiter instance
rate_limiter = RateLimiter(
    tokens_per_minute=60,  # 60 requests per minute
    burst_size=10,  # Allow bursts of 10 requests
)
