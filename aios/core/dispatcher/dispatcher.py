class Dispatcher:

    def __init__(self):
        self._handlers = {}

    def register(self, key, handler):
        self._handlers[key] = handler
        return handler

    def unregister(self, key):
        return self._handlers.pop(key, None)

    def dispatch(self, key, *args, **kwargs):
        handler = self._handlers[key]
        if hasattr(handler, "execute"):
            return handler.execute(*args, **kwargs)
        return handler(*args, **kwargs)

    def keys(self):
        return tuple(self._handlers)

    def clear(self):
        self._handlers.clear()
