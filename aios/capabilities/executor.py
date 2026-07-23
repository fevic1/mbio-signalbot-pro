from time import perf_counter

from aios.providers.router import chat
from aios.providers.types import ProviderRequest


class CapabilityExecutor:


    def execute(
        self,
        capability,
    ):

        request = ProviderRequest(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Execute capability: "
                        f"{capability}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Perform {capability} "
                        "and return structured output."
                    ),
                },
            ]
        )


        start = perf_counter()

        response = chat(
            request
        )

        latency = perf_counter() - start


        return {
            "capability": capability,
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
            "latency": latency,
            "cost": 0,
            "messages": request.messages,
        }
