from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class NodeStore(Generic[T]):
    def __init__(self):
        self._nodes: dict[str, T] = {}

    def add(self, node: T):
        self._nodes[node.name] = node

    def remove(self, name: str):
        self._nodes.pop(name, None)

    def get(self, name: str):
        return self._nodes.get(name)

    def values(self):
        return self._nodes.values()

    def items(self):
        return self._nodes.items()

    def keys(self):
        return self._nodes.keys()

    def clear(self):
        self._nodes.clear()

    def __contains__(self, name: str):
        return name in self._nodes

    def __getitem__(self, name: str):
        return self._nodes[name]

    def __setitem__(self, name: str, node: T):
        self._nodes[name] = node

    def __iter__(self) -> Iterator[T]:
        return iter(self._nodes.values())

    def __len__(self):
        return len(self._nodes)
