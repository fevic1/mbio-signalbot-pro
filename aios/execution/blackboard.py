from threading import RLock
from copy import deepcopy


class Blackboard:
    """
    Shared workspace between all agents.

    Agents never pass nested dictionaries to each other.
    Everything is written and read from the blackboard.
    """

    def __init__(self):
        self._data = {}
        self._lock = RLock()

    def store(self, key: str, value):
        with self._lock:
            self._data[key] = deepcopy(value)

    def read(self, key: str, default=None):
        with self._lock:
            return deepcopy(self._data.get(key, default))

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def update(self, key: str, values: dict):
        with self._lock:
            current = self._data.get(key, {})
            if not isinstance(current, dict):
                current = {}
            current.update(deepcopy(values))
            self._data[key] = current

    def delete(self, key: str):
        with self._lock:
            self._data.pop(key, None)

    def clear(self):
        with self._lock:
            self._data.clear()

    def snapshot(self):
        with self._lock:
            return deepcopy(self._data)
