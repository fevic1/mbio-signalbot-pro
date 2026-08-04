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
    compiler_latency: float = 0.0
    provider_latency: float = 0.0
    tool_latency: float = 0.0
    verification_latency: float = 0.0
    total_latency: float = 0.0
    estimated_cost: float = 0.0
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    verification_score: float = 0.0
    verification_passed: bool = False
    verification_report: dict[str, Any] = field(default_factory=dict)

    cost: float = 0.0

    route_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
