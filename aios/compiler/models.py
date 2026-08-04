from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TokenBudget:
    estimated_prompt_tokens: int = 0
    max_prompt_tokens: int = 0
    max_completion_tokens: int = 0
    reserve_tokens: int = 0


@dataclass(frozen=True, slots=True)
class ProviderHints:
    preferred_provider: str | None = None
    preferred_model: str | None = None
    prefers_speed: bool = False
    prefers_reasoning: bool = False
    max_cost: float | None = None


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    tools_called: tuple[str, ...] = ()
    sources: tuple[Any, ...] = ()
    verification: tuple[Any, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CompiledContext:
    messages: tuple[dict[str, Any], ...]
    memory: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    context: CompiledContext
    token_budget: TokenBudget
    provider_hints: ProviderHints
    evidence: EvidenceBundle
