"""
ai/ai_client.py — Institutional AI client with circuit breaker, retries, and caching.
"""
import asyncio
import logging
import os
import time
from functools import wraps
from typing import Callable, Dict, Optional

import backoff
from circuitbreaker import circuit

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}
CACHE_TTL = 300  # 5 minutes

def cached(ttl: int = CACHE_TTL):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            if cache_key in _cache:
                if time.time() - _cache_timestamps[cache_key] < ttl:
                    logger.debug(f"Cache hit: {cache_key}")
                    return _cache[cache_key]
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = time.time()
            
            return result
        return wrapper
    return decorator

class CircuitBreaker:
    """Circuit breaker pattern for AI providers."""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def allow_request(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"🔄 Circuit breaker HALF_OPEN")
                return True
            return False
        return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"🚨 Circuit breaker OPEN: {self.failure_count} failures")

# Circuit breakers per provider
_circuit_breakers = {
    "groq": CircuitBreaker(),
    "cerebras": CircuitBreaker(),
    "openrouter": CircuitBreaker(),
}

def get_circuit_breaker(provider: str) -> CircuitBreaker:
    """Get circuit breaker for a provider."""
    return _circuit_breakers.get(provider, CircuitBreaker())

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    async def acquire(self):
        """Wait until a call is allowed."""
        while True:
            now = time.time()
            # Remove old calls
            self.calls = [t for t in self.calls if now - t < self.period]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return
            
            # Wait until oldest call expires
            wait_time = self.period - (now - self.calls[0])
            if wait_time > 0:
                logger.debug(f"⏳ Rate limit: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

# Rate limiters per provider
_rate_limiters = {
    "groq": RateLimiter(max_calls=30, period=60),
    "cerebras": RateLimiter(max_calls=10, period=60),
    "openrouter": RateLimiter(max_calls=20, period=60),
}

async def call_ai_provider(
    provider: str,
    client,
    messages: list,
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 500,
    response_format: Optional[dict] = None,
) -> Optional[dict]:
    """
    Call AI provider with circuit breaker, rate limiting, and retries.
    """
    breaker = get_circuit_breaker(provider)
    limiter = _rate_limiters.get(provider, RateLimiter(30, 60))
    
    # Check circuit breaker
    if not breaker.allow_request():
        logger.warning(f"⚠️ Circuit breaker OPEN for {provider}")
        return None
    
    # Rate limiting
    await limiter.acquire()
    
    # Retry with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30,
        on_backoff=lambda details: logger.warning(
            f"Retry {details['tries']} for {provider}: {details.get('exception')}"
        )
    )
    async def _call():
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    try:
        content = await _call()
        breaker.record_success()
        return {"content": content, "provider": provider}
    except Exception as e:
        breaker.record_failure()
        logger.error(f"❌ AI call failed for {provider}: {e}")
        return None

def fallback_signal(symbol: str) -> dict:
    """Generate fallback signal when AI fails."""
    logger.warning(f"⚠️ Using fallback signal for {symbol}")
    return {
        "signal": "HOLD",
        "confidence": 30,
        "reasoning": "AI unavailable - using conservative fallback",
        "provider": "fallback"
    }
