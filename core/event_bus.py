
"""
MBIO Event Bus
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable

Handler = Callable[[dict], Awaitable[None]]

class EventBus:

    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, event: str, handler: Handler):
        if handler not in self._subs[event]:
            self._subs[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler):
        if handler in self._subs[event]:
            self._subs[event].remove(handler)

    async def publish(self, event: str, payload: dict[str, Any]):
        handlers = list(self._subs.get(event, []))
        if not handlers:
            return

        await asyncio.gather(
            *(h(payload) for h in handlers),
            return_exceptions=True,
        )

bus = EventBus()

EVENT_THESIS_UPDATED = "strategy.thesis.updated"
EVENT_POSITION_CHANGED = "position.changed"
EVENT_POSITION_EXPAND = "position.expand"
EVENT_POSITION_EXIT = "position.exit"
EVENT_DCA_FILL = "dca.fill"
EVENT_ORDER_FILLED = "order.filled"
EVENT_ORDER_CANCELLED = "order.cancelled"
EVENT_RISK_ALERT = "risk.alert"


# Global singleton
event_bus = EventBus()
