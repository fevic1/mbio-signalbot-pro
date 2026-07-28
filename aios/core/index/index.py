from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Index(Generic[K, V]):

    def __init__(self):
        self._index: dict[K, V] = {}

    def add(self, key: K, value: V):
        self._index[key] = value
        return value

    def get(self, key: K, default=None):
        return self._index.get(key, default)

    def remove(self, key: K):
        return self._index.pop(key, None)

    def keys(self):
        return self._index.keys()

    def values(self):
        return self._index.values()

    def items(self):
        return self._index.items()

    def clear(self):
        self._index.clear()

    def __contains__(self, key):
        return key in self._index

    def __len__(self):
        return len(self._index)
