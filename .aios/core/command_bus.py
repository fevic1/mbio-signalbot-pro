#!/usr/bin/env python3

class CommandBus:

    def __init__(self):
        self._commands = {}

    def register(self, name, handler):
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")
        self._commands[name] = handler

    def unregister(self, name):
        self._commands.pop(name, None)

    def execute(self, name, *args, **kwargs):
        if name not in self._commands:
            raise KeyError(f"Unknown command '{name}'")
        return self._commands[name](*args, **kwargs)

    def exists(self, name):
        return name in self._commands

    def list(self):
        return sorted(self._commands.keys())


command_bus = CommandBus()


if __name__ == "__main__":

    def hello(name):
        return f"Hello {name}"

    command_bus.register("hello", hello)

    print(command_bus.execute("hello", "AIOS"))
    print(command_bus.list())
