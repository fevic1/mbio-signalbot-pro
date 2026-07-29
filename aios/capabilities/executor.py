import json
import re
from time import perf_counter

from aios.intelligence.llm_adapter import LLMAdapter
from aios.providers.router import chat
from aios.providers.router import provider_pool
from aios.providers.types import ProviderRequest
from aios.capabilities.policy import CapabilityPolicyEngine
from aios.capabilities.errors import CapabilityExecutionError

from .request import CapabilityRequest

class CapabilityExecutor:

    def __init__(
        self,
        system,
    ):
        self.system = system

        self.adapter = LLMAdapter(
            provider_pool,
            system,
        )

        self.policy = CapabilityPolicyEngine(
            provider_pool
        )

    def _get_capability_definition(self, name):

        registry = self.system.capability_registry

        if registry is None:
            raise CapabilityExecutionError(
                "Capability registry unavailable"
            )

        capability = registry.get(name)

        if capability is None:
            raise CapabilityExecutionError(
                f"Unknown capability: {name}"
            )

        return capability



    def _validate_capability_policy(
        self,
        capability,
    ):

        return self.policy.validate(
            capability
        )


    async def execute(
        self,
        request: CapabilityRequest,
    ):

        capability = self._get_capability_definition(
            request.capability
        )

        self._validate_capability_policy(
            capability
        )

        last_error = None

        for attempt in range(
            request.retry_limit + 1
        ):

            try:
                return await self._execute_once(
                    request,
                    attempt,
                )

            except Exception as error:
                last_error = error

        raise CapabilityExecutionError(
            f"{request.capability}: {last_error}"
        ) from last_error

    async def _execute_once(
        self,
        request: CapabilityRequest,
        attempt: int,
    ):

        prompt = self.adapter.build(
            request.capability,
            request,
        )

        provider_request = ProviderRequest(
            messages=[
                {
                    "role": "system",
                    "content": prompt["system"],
                },
                {
                    "role": "user",
                    "content": str(prompt["context"]),
                },
            ]
        )

        start = perf_counter()

        response = await chat(
            provider_request,
            event_bus=self.system.event_bus,
            capability=request.capability,
        )

        latency = perf_counter() - start

        content = response.content

        parsed = {}

        if isinstance(content, str):
            cleaned = re.sub(
                r"```json\\s*|```",
                "",
                content,
            )

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start != -1 and end > start:
                try:
                    parsed = json.loads(
                        cleaned[start:end + 1]
                    )
                except Exception:
                    parsed = {}

        content = response.content

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                pass

        final_content = parsed or content

        if isinstance(final_content, dict):

            confidence = final_content.get(
                "confidence"
            )

            if confidence is not None:

                if confidence == 0:
                    final_content["confidence"] = 0.5

                elif confidence > 1:
                    final_content["confidence"] = confidence / 100

        return {
            "success": True,
            "capability": request.capability,
            "provider": response.provider,
            "model": response.model,
            "content": final_content,
            "latency": latency,
            "cost": 0.0,
            "attempt": attempt,
        }
