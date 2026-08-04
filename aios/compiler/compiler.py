from .models import CompiledContext, ExecutionPlan
from .token_budget import TokenBudgetManager
from .provider_hints import ProviderHintsBuilder
from .evidence_bundle import EvidenceBuilder


class ContextCompiler:

    def __init__(self):
        self.tokens = TokenBudgetManager()
        self.providers = ProviderHintsBuilder()
        self.evidence = EvidenceBuilder()

    def compile(
        self,
        *,
        messages,
        capability,
        memory=None,
        metadata=None,
    ) -> ExecutionPlan:

        context = CompiledContext(
            messages=tuple(messages),
            memory=memory or {},
            metadata=metadata or {},
        )

        estimate = sum(
            len(str(m.get("content", ""))) // 4
            for m in messages
        )

        return ExecutionPlan(
            context=context,
            token_budget=self.tokens.build(estimate),
            provider_hints=self.providers.build(capability),
            evidence=self.evidence.empty(),
        )
