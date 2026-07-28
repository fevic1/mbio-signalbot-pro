#!/usr/bin/env python3

import json
from pathlib import Path


class StateManager:

    def __init__(self):
        self.path = Path(".aios/memory/state.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text("{}")

    def _load(self):
        with self.path.open() as f:
            return json.load(f)

    def _save(self, state):
        with self.path.open("w") as f:
            json.dump(state, f, indent=2)

    def get(self, key, default=None):
        state = self._load()
        return state.get(key, default)

    def set(self, key, value):
        state = self._load()
        state[key] = value
        self._save(state)

    def delete(self, key):
        state = self._load()

        if key in state:
            del state[key]
            self._save(state)

    def all(self):
        return self._load()

    def clear(self):
        self._save({})


state = StateManager()


if __name__ == "__main__":

    state.set("runtime", "running")
    state.set("plugin_count", 1)

    print(state.get("runtime"))
    print(state.all())
