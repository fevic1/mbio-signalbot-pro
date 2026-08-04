from .execution_plan import ExecutionPlan

try:
    import tiktoken
except Exception:
    tiktoken = None



class ContextCompiler:











    def _build_route_metadata(
        self,
        capability,
        provider_hints,
        token_budget,
    ):
        return {
            "compiler": "ContextCompiler",
            "compiler_version": "2.0",
            "capability": capability,
            "estimated_prompt_tokens":
                token_budget.estimated_prompt_tokens,
            "max_prompt_tokens":
                token_budget.max_prompt_tokens,
            "max_completion_tokens":
                token_budget.max_completion_tokens,
            "reserve_tokens":
                token_budget.reserve_tokens,
            "prefers_speed":
                provider_hints.prefers_speed,
            "prefers_reasoning":
                provider_hints.prefers_reasoning,
            "preferred_provider":
                provider_hints.preferred_provider,
            "preferred_model":
                provider_hints.preferred_model,
        }


    def _build_evidence_bundle(
        self,
        metadata,
    ):
        metadata = metadata or {}

        return EvidenceBundle(
            tools_called=tuple(
                metadata.get("tool_plan", ())
            ),
            sources=tuple(
                metadata.get("tool_results", ())
            ),
        )


    def _build_provider_hints(
        self,
        capability,
        messages,
    ):
        text = " ".join(
            str(m.get("content", "")).lower()
            for m in messages
        )

        reasoning = any(
            x in text
            for x in (
                "analyze",
                "reason",
                "compare",
                "research",
                "verify",
                "audit",
            )
        )

        speed = capability in {
            "chat",
            "assistant",
            "completion",
        }

        return ProviderHints(
            prefers_reasoning=reasoning,
            prefers_speed=speed,
        )


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
