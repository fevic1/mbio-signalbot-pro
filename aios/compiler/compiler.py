from .execution_plan import ExecutionPlan

try:
    import tiktoken
except Exception:
    tiktoken = None



class ContextCompiler:





    def _compress_messages(
        self,
        messages,
        budget,
    ):
        if self._estimate_tokens(messages) <= budget.max_prompt_tokens:
            return messages

        compressed = [messages[0]]

        if len(messages) > 2:
            summary = "\n".join(
                str(m.get("content", ""))[:160]
                for m in messages[1:-1]
            )

            compressed.append(
                {
                    "role": "system",
                    "content":
                        "Conversation Summary:\n" + summary,
                }
            )

        compressed.append(messages[-1])

        return compressed


    def _trim_messages(
        self,
        messages,
        budget,
    ):
        trimmed = list(messages)

        while (
            self._estimate_tokens(trimmed)
            > budget.max_prompt_tokens
            and len(trimmed) > 2
        ):
            trimmed.pop(1)

        return tuple(trimmed)

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
            messages=self._trim_messages(
                self._compress_messages(
                    messages,
                    token_budget,
                ),
                token_budget,
            ),
            token_budget=token_budget,
            provider_hints=provider_hints,
            evidence=evidence,
            metadata=metadata or {},
        )
