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
    route: tuple[str, ...] = ()
    selected_provider: str | None = None
    selected_model: str | None = None
    compiler: dict[str, Any] = field(default_factory=dict)
    provider_hints: dict[str, Any] = field(default_factory=dict)
    token_budget: dict[str, Any] = field(default_factory=dict)
    execution_evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderResponse:
    provider: str
    model: str
    content: str
    raw: dict[str, Any]

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    latency: float = 0.0
    compiler_latency: float = 0.0
    provider_latency: float = 0.0
    tool_latency: float = 0.0
    verification_latency: float = 0.0
    total_latency: float = 0.0
    cost: float = 0.0

    route_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderHealth:
    provider: str
    healthy: bool
