#!/usr/bin/env python3

class QueryBus:

    def __init__(self):
        self._queries = {}

    def register(self, name, handler):
        if name in self._queries:
            raise ValueError(f"Query '{name}' already registered")
        self._queries[name] = handler

    def unregister(self, name):
        self._queries.pop(name, None)

    def execute(self, name, *args, **kwargs):
        if name not in self._queries:
            raise KeyError(f"Unknown query '{name}'")
        return self._queries[name](*args, **kwargs)

    def exists(self, name):
        return name in self._queries

    def list(self):
        return sorted(self._queries.keys())


query_bus = QueryBus()


if __name__ == "__main__":

    users = {
        1: "Alice",
        2: "Bob",
    }

    def get_user(user_id):
        return users.get(user_id)

    query_bus.register("user.get", get_user)

    print(query_bus.execute("user.get", 1))
    print(query_bus.list())
