class RuntimeAPIGateway:

    def __init__(self, kernel):
        self._kernel = kernel
        self._routes = {}

    def register(self, name: str, handler):
        self._routes[name] = handler
        return handler

    def unregister(self, name: str):
        return self._routes.pop(name, None)

    def call(self, name: str, *args, **kwargs):
        handler = self._routes[name]
        return handler(*args, **kwargs)

    def routes(self):
        return tuple(sorted(self._routes))

    def export(self):
        return {
            name: getattr(
                handler,
                "__name__",
                type(handler).__name__,
            )
            for name, handler in self._routes.items()
        }

    def clear(self):
        self._routes.clear()

    def __contains__(self, name):
        return name in self._routes

    def __len__(self):
        return len(self._routes)
