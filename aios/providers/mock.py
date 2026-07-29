from .base import BaseProvider
from .types import ProviderRequest, ProviderResponse


class MockProvider(BaseProvider):

    name = "mock"

    def available(self):
        return True

    def health(self):
        return True

    async def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        return ProviderResponse(
            provider=self.name,
            model="mock-model",
            content=(
                "AIOS mock response: "
                "capability execution successful"
            ),
            raw={
                "mode": "test"
            },
        )

    def models(self):
        return [
            "mock-model"
        ]
