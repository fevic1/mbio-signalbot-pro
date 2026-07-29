from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Factory(Generic[T]):

    def __init__(self):
        self._builders: dict[str, Callable[..., T]] = {}

    def register(self, name: str, builder: Callable[..., T]):
        self._builders[name] = builder
        return builder

    def create(self, name: str, *args, **kwargs):
        return self._builders[name](*args, **kwargs)

    def names(self):
        return tuple(self._builders)
