import os
import requests

from .base import BaseProvider
from .types import ProviderResponse
from .exceptions import AuthenticationError


class CerebrasProvider(BaseProvider):

    name = "cerebras"

    def __init__(self):
        self.key = os.getenv("CEREBRAS_API_KEY")
        self.model = os.getenv(
            "CEREBRAS_MODEL",
            "llama-4-scout-17b-16e-instruct"
        )

    def chat(self, request):
        if not self.key:
            raise AuthenticationError("CEREBRAS_API_KEY not configured")

        r = requests.post(
            "https://api.cerebras.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
            timeout=60,
        )

        r.raise_for_status()

        data = r.json()

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            content=data["choices"][0]["message"]["content"],
            raw=data,
        )

    def health(self) -> bool:
        return self.key is not None

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
