#!/usr/bin/env python3

from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event: str, handler: Callable):
        self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable):
        if handler in self._subscribers[event]:
            self._subscribers[event].remove(handler)

    def publish(self, event: str, payload=None):
        for handler in self._subscribers.get(event, []):
            handler(payload)


event_bus = EventBus()


if __name__ == "__main__":

    def listener(data):
        print(f"Received: {data}")

    event_bus.subscribe("startup", listener)
    event_bus.publish("startup", {"plugin": "superpowers"})
