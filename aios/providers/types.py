from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderRequest:
    messages: list
    model: str | None = None
    provider: str | None = None
    temperature: float = 0.2
    max_tokens: int = 2048
    tools: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ProviderResponse:
    provider: str
    model: str
    content: str
    raw: dict[str, Any]


@dataclass(slots=True)
class ProviderHealth:
    provider: str
    healthy: bool
