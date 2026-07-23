from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProviderResponse:
    provider: str
    model: str
    content: str
    raw: dict[str, Any]


class BaseProvider(ABC):
    name = ""

    @abstractmethod
    def available(self) -> bool:
        """Return True if this provider can be used."""
        ...

    @abstractmethod
    async def chat(self, request) -> ProviderResponse:
        """Execute a chat completion."""
        ...

    @abstractmethod
    def health(self) -> bool:
        """Basic health check."""
        ...

    @abstractmethod
    def models(self) -> list[str]:
        """Supported models."""
        ...
