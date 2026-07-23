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

        return chat(request)
