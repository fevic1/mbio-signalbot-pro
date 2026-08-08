
"""
MBIO Global Exchange Rate Limiter
"""

from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:

    def __init__(self, max_calls: int = 40, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()

            while self.calls and now - self.calls[0] > self.period:
                self.calls.popleft()

            if len(self.calls) >= self.max_calls:
                wait = self.period - (now - self.calls[0])
                if wait > 0:
                    await asyncio.sleep(wait)

                now = time.monotonic()
                while self.calls and now - self.calls[0] > self.period:
                    self.calls.popleft()

            self.calls.append(time.monotonic())

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


exchange_rate_limiter = RateLimiter()


# Backward compatibility
rate_limiter = exchange_rate_limiter
