from .models import TokenBudget


class TokenBudgetManager:

    DEFAULT_CONTEXT = 32768
    DEFAULT_RESERVE = 2048

    def build(
        self,
        estimated_prompt_tokens: int,
        context_limit: int | None = None,
    ) -> TokenBudget:

        limit = context_limit or self.DEFAULT_CONTEXT

        completion = max(
            512,
            limit - estimated_prompt_tokens - self.DEFAULT_RESERVE,
        )

        return TokenBudget(
            estimated_prompt_tokens=estimated_prompt_tokens,
            max_prompt_tokens=limit,
            max_completion_tokens=completion,
            reserve_tokens=self.DEFAULT_RESERVE,
        )
