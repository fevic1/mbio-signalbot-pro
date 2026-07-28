from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class Store(Generic[T]):

    def __init__(self):
        self._items: dict[str, T] = {}

    def add(self, key: str, value: T):
        self._items[key] = value
        return value

    def get(self, key: str, default=None):
        return self._items.get(key, default)

    def remove(self, key: str):
        return self._items.pop(key, None)

    def values(self) -> Iterable[T]:
        return self._items.values()

    def items(self):
        return self._items.items()

    def clear(self):
        self._items.clear()

    def __contains__(self, key):
        return key in self._items

    def __len__(self):
        return len(self._items)
