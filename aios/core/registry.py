from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self):
        self._items: dict[str, T] = {}

    def register(self, name: str, item: T):
        self._items[name] = item
        return item

    def unregister(self, name: str):
        return self._items.pop(name, None)

    def get(self, name: str):
        return self._items.get(name)

    def all(self):
        return self._items.values()

    def items(self):
        return self._items.items()

    def __contains__(self, name: str):
        return name in self._items

    def __len__(self):
        return len(self._items)

    def clear(self):
        self._items.clear()

    def values(self):
        return self._items.values()

    def keys(self):
        return self._items.keys()
