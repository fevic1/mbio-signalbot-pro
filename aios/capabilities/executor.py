from time import perf_counter

from aios.providers.router import chat
from aios.providers.types import ProviderRequest

from .request import CapabilityRequest


class CapabilityExecutionError(Exception):
    pass


class CapabilityExecutor:

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

        provider_request = ProviderRequest(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Execute capability: "
                        f"{request.capability}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Capability: {request.capability}\n"
                        f"Permission: {request.permission}\n"
                        f"Attempt: {attempt}\n"
                        f"Context: {request.context}\n"
                        "Return structured output."
                    ),
                },
            ]
        )

        start = perf_counter()

        response = chat(provider_request)

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
