from dataclasses import dataclass
from typing import Any

@dataclass
class ProviderRequest:
    messages: list
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 2048

@dataclass
class ProviderResponse:
    provider: str
    model: str
    content: str
    raw: Any = None

@dataclass
class ProviderHealth:
    provider: str
    healthy: bool
