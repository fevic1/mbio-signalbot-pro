from .event import RuntimeEvent


class RuntimeEventBus:

    def __init__(self):
        self._handlers: dict[str, list] = {}

    def subscribe(self, name: str, handler):
        self._handlers.setdefault(name, []).append(handler)
        return handler

    def unsubscribe(self, name: str, handler):
        handlers = self._handlers.get(name, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: RuntimeEvent):
        for handler in self._handlers.get(event.name, ()):
            handler(event)

    def clear(self):
        self._handlers.clear()
