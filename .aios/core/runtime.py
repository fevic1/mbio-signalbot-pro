#!/usr/bin/env python3

from threading import RLock


class Runtime:

    def __init__(self):
        self._lock = RLock()
        self._state = "created"

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        with self._lock:
            self._state = state

    def is_created(self):
        return self._state == "created"

    def is_starting(self):
        return self._state == "starting"

    def is_running(self):
        return self._state == "running"

    def is_stopping(self):
        return self._state == "stopping"

    def is_stopped(self):
        return self._state == "stopped"

    def health(self):
        return {
            "state": self._state
        }


runtime = Runtime()


if __name__ == "__main__":

    print(runtime.health())

    runtime.set_state("starting")
    print(runtime.health())

    runtime.set_state("running")
    print(runtime.health())

    runtime.set_state("stopping")
    print(runtime.health())

    runtime.set_state("stopped")
    print(runtime.health())
