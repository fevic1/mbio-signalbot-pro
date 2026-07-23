from time import perf_counter

from aios.intelligence.llm_adapter import LLMAdapter
from aios.providers.router import chat
from aios.providers.router import provider_pool
from aios.providers.types import ProviderRequest

from .request import CapabilityRequest


class CapabilityExecutionError(Exception):
    pass


class CapabilityExecutor:

    def __init__(self):
        self.adapter = LLMAdapter(provider_pool)

    def execute(
        self,
        request: CapabilityRequest,
    ):

        last_error = None

        for attempt in range(
            request.retry_limit + 1
        ):

            try:
                return self._execute_once(
                    request,
                    attempt,
                )

            except Exception as error:
                last_error = error

        raise CapabilityExecutionError(
            f"{request.capability}: {last_error}"
        ) from last_error

    def _execute_once(
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

        response = chat(
            provider_request
        )

        latency = perf_counter() - start

        return {
            "success": True,
            "capability": request.capability,
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
            "latency": latency,
            "cost": 0.0,
            "attempt": attempt,
        }
