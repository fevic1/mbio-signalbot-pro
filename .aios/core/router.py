#!/usr/bin/env python3

class Router:

    def __init__(self):
        self._routes = {}

    def register(self, route, handler):
        if route in self._routes:
            raise ValueError(f"Route '{route}' already exists")
        self._routes[route] = handler

    def unregister(self, route):
        self._routes.pop(route, None)

    def dispatch(self, route, *args, **kwargs):
        if route not in self._routes:
            raise KeyError(f"Unknown route '{route}'")
        return self._routes[route](*args, **kwargs)

    def exists(self, route):
        return route in self._routes

    def list(self):
        return sorted(self._routes.keys())


router = Router()


if __name__ == "__main__":

    def echo(message):
        return f"echo: {message}"

    router.register("echo", echo)

    print(router.dispatch("echo", "AIOS"))
    print(router.list())
