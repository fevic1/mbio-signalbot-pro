"""
core/executor_utils.py — Non-blocking wrappers for sync HLExecutor methods.
Follows institutional pattern from strategy_manager.py:141.
Per CODING_STANDARD: No blocking async. Every external call: timeout.
"""
import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Default timeout for all executor calls (seconds)
DEFAULT_EXECUTOR_TIMEOUT = 10.0


async def run_executor_method(method: Callable[..., Any], *args, timeout: float = DEFAULT_EXECUTOR_TIMEOUT, **kwargs) -> Any:
    """
    Run a synchronous HLExecutor method in a thread pool without blocking the event loop.
    
    Args:
        method: Bound method to execute (e.g., executor.get_open_positions)
        *args: Positional arguments for the method
        timeout: Maximum seconds to wait (default 10s)
        **kwargs: Keyword arguments for the method
    
    Returns:
        Method return value
        
    Raises:
        asyncio.TimeoutError: If method exceeds timeout
        Exception: Re-raises any exception from the method
    """
    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: method(*args, **kwargs)),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"❌ Executor method {method.__name__} timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"❌ Executor method {method.__name__} failed: {type(e).__name__}: {e}")
        raise
