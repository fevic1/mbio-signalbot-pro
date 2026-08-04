from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIOSRequest:

    capability: str

    messages: list

    intent: str | None = None

    memory: dict[str, Any] = field(
        default_factory=dict
    )

    tools: list = field(
        default_factory=list
    )

    constraints: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class AIOSResponse:

    provider: str

    model: str

    content: Any

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    latency: float = 0.0

    cost: float = 0.0

    route_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
