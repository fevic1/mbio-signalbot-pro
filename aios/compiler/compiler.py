from .execution_plan import ExecutionPlan

try:
    import tiktoken
except Exception:
    tiktoken = None



class ContextCompiler:

    def _estimate_tokens(self, messages):
        if tiktoken:
            try:
                enc = tiktoken.get_encoding("cl100k_base")
                return int(sum(
                    len(enc.encode(str(m.get("content", ""))))
                    for m in messages
                ))
            except Exception:
                pass

        return int(sum(
            max(1, len(str(m.get("content", "")).split())) * 1.35
            for m in messages
        ))


    def compile(
        self,
        capability,
        messages,
        *,
        token_budget,
        provider_hints,
        evidence,
        metadata=None,
    ):

        return ExecutionPlan(
            capability=capability,
            messages=tuple(messages),
            token_budget=token_budget,
            provider_hints=provider_hints,
            evidence=evidence,
            metadata=metadata or {},
        )
