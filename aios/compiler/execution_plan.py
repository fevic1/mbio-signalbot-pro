from dataclasses import dataclass, field
from typing import Any

from .models import (
    TokenBudget,
    ProviderHints,
    EvidenceBundle,
)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    capability: str
    messages: tuple[dict, ...]
    token_budget: TokenBudget
    provider_hints: ProviderHints
    evidence: EvidenceBundle
    metadata: dict[str, Any] = field(default_factory=dict)
