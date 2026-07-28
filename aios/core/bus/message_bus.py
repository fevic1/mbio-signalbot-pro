class MessageBus:

    def __init__(self):
        self._handlers = {}

    def subscribe(self, topic, handler):
        self._handlers.setdefault(topic, []).append(handler)
        return handler

    def unsubscribe(self, topic, handler):
        handlers = self._handlers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, topic, message):
        for handler in self._handlers.get(topic, ()):
            handler(message)

    def clear(self):
        self._handlers.clear()
