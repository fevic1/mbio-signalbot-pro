from .execution_plan import ExecutionPlan

try:
    import tiktoken
except Exception:
    tiktoken = None



class ContextCompiler:





















    def _cache_key(
        self,
        plan,
    ):
        return (
            plan.metadata.get(
                "execution_fingerprint"
            ),
            plan.capability,
        )


    def _fingerprint_plan(
        self,
        plan,
    ):
        import hashlib
        import json

        payload = {
            "capability": plan.capability,
            "messages": plan.messages,
            "token_budget": plan.token_budget.__dict__,
            "provider_hints": plan.provider_hints.__dict__,
            "evidence": {
                "tools_called": list(plan.evidence.tools_called),
                "sources": list(plan.evidence.sources),
            },
        }

        return hashlib.sha256(
            json.dumps(
                payload,
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()


    def _freeze_messages(
        self,
        messages,
    ):
        return tuple(
            {
                k: v
                for k, v in message.items()
            }
            for message in messages
        )


    def _validate_plan(
        self,
        plan,
    ):
        if (
            plan.token_budget.estimated_prompt_tokens
            > plan.token_budget.max_prompt_tokens
        ):
            raise ValueError(
                "ExecutionPlan exceeds prompt budget."
            )

        plan = self._validate_plan(plan)

        plan.metadata["cache_key"] = self._cache_key(plan)

        plan.metadata["execution_fingerprint"] = (
            self._fingerprint_plan(plan)
        )

        plan.metadata["execution_signature"] = (
            self._execution_signature(plan)
        )

        plan.metadata["runtime_contract"] = (
            self._runtime_contract(plan)
        )

        plan.metadata["compiler_health"] = (
            self._compiler_health(plan)
        )

        plan.metadata["compile_summary"] = (
            self._compile_summary(plan)
        )

        plan.metadata["compiler_manifest"] = (
            self._compiler_manifest(plan)
        )

        return plan

        return plan


    def _score_route(
        self,
        provider_hints,
        token_budget,
    ):
        score = 0

        if provider_hints.prefers_reasoning:
            score += 40

        if provider_hints.prefers_speed:
            score += 20

        if token_budget.estimated_prompt_tokens > 8000:
            score += 20

        if token_budget.estimated_prompt_tokens > 16000:
            score += 20

        return min(score, 100)


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
            "route_score":
                self._score_route(
                    provider_hints,
                    token_budget,
                ),
            "estimated_cost":
                self._estimate_cost(
                    provider_hints,
                    token_budget,
                ),
            "estimated_latency":
                self._estimate_latency(
                    provider_hints,
                    token_budget,
                ),
            "execution_quality":
                self._execution_quality(
                    provider_hints,
                    token_budget,
                ),
            "execution_readiness":
                self._execution_readiness(
                    token_budget,
                    provider_hints,
                ),
            "route_score":
                self._score_route(
                    provider_hints,
                    token_budget,
                ),
            "estimated_cost":
                self._estimate_cost(
                    provider_hints,
                    token_budget,
                ),
            "estimated_latency":
                self._estimate_latency(
                    provider_hints,
                    token_budget,
                ),
            "execution_quality":
                self._execution_quality(
                    provider_hints,
                    token_budget,
                ),
            "execution_readiness":
                self._execution_readiness(
                    token_budget,
                    provider_hints,
                ),
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






















    def _compiler_manifest(
        self,
        plan,
    ):
        return {
            "version": "1.0",
            "immutable": True,
            "validated": True,
            "compiler_health":
                plan.metadata.get(
                    "compiler_health"
                ),
            "runtime_contract":
                plan.metadata.get(
                    "runtime_contract"
                ),
            "execution_signature":
                plan.metadata.get(
                    "execution_signature"
                ),
            "compile_summary":
                plan.metadata.get(
                    "compile_summary"
                ),
            "fingerprint":
                plan.metadata.get(
                    "execution_fingerprint"
                ),
            "cache_key":
                plan.metadata.get(
                    "cache_key"
                ),
        }


    def _compile_summary(
        self,
        plan,
    ):
        return {
            "provider":
                plan.provider_hints.preferred_provider,
            "model":
                plan.provider_hints.preferred_model,
            "prompt_tokens":
                plan.token_budget.estimated_prompt_tokens,
            "max_prompt_tokens":
                plan.token_budget.max_prompt_tokens,
            "max_completion_tokens":
                plan.token_budget.max_completion_tokens,
            "estimated_cost":
                plan.metadata.get(
                    "estimated_cost"
                ),
            "estimated_latency":
                plan.metadata.get(
                    "estimated_latency"
                ),
            "route_score":
                plan.metadata.get(
                    "route_score"
                ),
            "execution_quality":
                plan.metadata.get(
                    "execution_quality"
                ),
            "execution_readiness":
                plan.metadata.get(
                    "execution_readiness"
                ),
            "fingerprint":
                plan.metadata.get(
                    "execution_fingerprint"
                ),
            "cache_key":
                plan.metadata.get(
                    "cache_key"
                ),
        }


    def _compiler_health(
        self,
        plan,
    ):
        diagnostics = plan.metadata.get(
            "compiler_diagnostics",
            {},
        )

        readiness = plan.metadata.get(
            "execution_readiness",
            0,
        )

        quality = plan.metadata.get(
            "execution_quality",
            0,
        )

        route = plan.metadata.get(
            "route_score",
            0,
        )

        return {
            "healthy": (
                readiness >= 90 and
                quality >= 90 and
                route >= 80
            ),
            "readiness": readiness,
            "quality": quality,
            "route_score": route,
            "diagnostics": diagnostics,
        }


    def _runtime_contract(
        self,
        plan,
    ):
        return {
            "immutable": True,
            "validated": True,
            "fingerprint":
                plan.metadata.get(
                    "execution_fingerprint"
                ),
            "cache_key":
                plan.metadata.get(
                    "cache_key"
                ),
            "route_score":
                plan.metadata.get(
                    "route_score"
                ),
            "estimated_cost":
                plan.metadata.get(
                    "estimated_cost"
                ),
            "estimated_latency":
                plan.metadata.get(
                    "estimated_latency"
                ),
            "execution_quality":
                plan.metadata.get(
                    "execution_quality"
                ),
            "execution_readiness":
                plan.metadata.get(
                    "execution_readiness"
                ),
        }


    def _execution_signature(
        self,
        plan,
    ):
        return {
            "fingerprint":
                plan.metadata.get(
                    "execution_fingerprint"
                ),
            "cache_key":
                plan.metadata.get(
                    "cache_key"
                ),
            "route_score":
                plan.metadata.get(
                    "route_score"
                ),
            "execution_quality":
                plan.metadata.get(
                    "execution_quality"
                ),
            "execution_readiness":
                plan.metadata.get(
                    "execution_readiness"
                ),
        }


    def _execution_readiness(
        self,
        token_budget,
        provider_hints,
    ):
        score = 100

        if token_budget.estimated_prompt_tokens > token_budget.max_prompt_tokens:
            score -= 50

        if provider_hints.prefers_reasoning:
            score += 3

        if provider_hints.prefers_speed:
            score += 2

        return max(0, min(score, 100))


    def _execution_quality(
        self,
        provider_hints,
        token_budget,
    ):
        quality = 100

        if token_budget.estimated_prompt_tokens > 12000:
            quality -= 5

        if token_budget.estimated_prompt_tokens > 20000:
            quality -= 5

        if provider_hints.prefers_speed:
            quality -= 2

        if provider_hints.prefers_reasoning:
            quality += 2

        return max(0, min(100, quality))


    def _estimate_latency(
        self,
        provider_hints,
        token_budget,
    ):
        latency = 0.20

        latency += (
            token_budget.estimated_prompt_tokens
            / 10000
        ) * 0.30

        if provider_hints.prefers_reasoning:
            latency += 0.80

        if provider_hints.prefers_speed:
            latency -= 0.10

        return round(max(latency, 0.05), 3)


    def _estimate_cost(
        self,
        provider_hints,
        token_budget,
    ):
        rate = 0.000002

        if provider_hints.prefers_reasoning:
            rate *= 2.5

        estimated = (
            token_budget.estimated_prompt_tokens +
            token_budget.max_completion_tokens
        ) * rate

        return round(estimated, 6)


    def _optimize_token_budget(
        self,
        token_budget,
        provider_hints,
    ):
        prompt = token_budget.max_prompt_tokens
        completion = token_budget.max_completion_tokens
        reserve = token_budget.reserve_tokens

        if provider_hints.prefers_reasoning:
            completion = max(completion, 8192)

        if provider_hints.prefers_speed:
            completion = min(completion, 2048)

        return TokenBudget(
            estimated_prompt_tokens=token_budget.estimated_prompt_tokens,
            max_prompt_tokens=prompt,
            max_completion_tokens=completion,
            reserve_tokens=reserve,
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




    def _normalize_messages(
        self,
        messages,
    ):
        normalized = []

        for message in messages:
            normalized.append(
                {
                    "role": str(
                        message.get(
                            "role",
                            "user",
                        )
                    ),
                    "content": str(
                        message.get(
                            "content",
                            "",
                        )
                    ).strip(),
                }
            )

        return normalized


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

        plan = ExecutionPlan(
            capability=capability,
            messages=self._freeze_messages(self._normalize_messages(self._trim_messages(
                self._compress_messages(
                    messages,
                    token_budget,
                ),
                token_budget,
            ))),
            token_budget=token_budget,
            provider_hints=provider_hints,
            evidence=evidence,
            metadata=metadata or {},
        )
