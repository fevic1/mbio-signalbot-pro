import os
import requests

from .base import BaseProvider
from .types import ProviderRequest, ProviderResponse
from .exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    TimeoutError,
)


class CerebrasProvider(BaseProvider):

    name = "cerebras"

    def __init__(self):
        self.key = os.getenv("CEREBRAS_API_KEY")

        self.model = os.getenv(
            "CEREBRAS_MODEL_NAME",
            "llama-4-scout-17b-16e-instruct",
        )

        self.url = "https://api.cerebras.ai/v1/chat/completions"

    def chat(self, request: ProviderRequest) -> ProviderResponse:

        if not self.key:
            from .exceptions import AuthenticationError
            raise AuthenticationError("CEREBRAS_API_KEY not configured")
        try:

            r = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": request.model or self.model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                },
                timeout=60,
            )

        except requests.Timeout as e:
            raise TimeoutError(str(e))

        except requests.RequestException as e:
            raise ProviderError(str(e))

        if r.status_code == 401:
            raise AuthenticationError(r.text)

        if r.status_code == 429:
            raise RateLimitError(r.text)

        if r.status_code >= 400:
            raise ProviderError(r.text)

        data = r.json()

        return ProviderResponse(
            provider=self.name,
            model=data.get("model", request.model or self.model),
            content=data["choices"][0]["message"]["content"],
            raw=data,
        )

    def health(self):
        return bool(self.key)

    def models(self):
        return [
            self.model,
        ]

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
