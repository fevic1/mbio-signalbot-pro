from typing import Generic, Iterable, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Catalog(Generic[K, V]):

    def __init__(self):
        self._entries: dict[K, V] = {}

    def register(self, key: K, value: V):
        self._entries[key] = value
        return value

    def unregister(self, key: K):
        return self._entries.pop(key, None)

    def get(self, key: K, default=None):
        return self._entries.get(key, default)

    def values(self) -> Iterable[V]:
        return self._entries.values()

    def items(self):
        return self._entries.items()

    def keys(self):
        return self._entries.keys()

    def clear(self):
        self._entries.clear()

    def __contains__(self, key):
        return key in self._entries

    def __len__(self):
        return len(self._entries)
