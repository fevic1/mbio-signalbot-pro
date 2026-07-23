from time import perf_counter

from aios.providers.router import chat
from aios.providers.types import ProviderRequest

from .request import CapabilityRequest


class CapabilityExecutor:


    def execute(
        self,
        request: CapabilityRequest,
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
                        f"Context: {request.context}\n"
                        "Return structured output."
                    ),
                },
            ]
        )


        start = perf_counter()

        response = chat(
            provider_request
        )

        latency = perf_counter() - start


        return {
            "capability": request.capability,
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
            "latency": latency,
            "cost": 0,
            "retry_limit": request.retry_limit,
        }
