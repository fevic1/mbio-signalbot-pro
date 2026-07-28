from typing import Generic, TypeVar

T = TypeVar("T")


class Service(Generic[T]):

    def __init__(self, backend: T):
        self.backend = backend

    def __getattr__(self, name):
        return getattr(self.backend, name)
