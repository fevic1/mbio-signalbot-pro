from time import perf_counter
import os

from .base import BaseProvider
from .exceptions import AuthenticationError
from .transport import http
from .types import ProviderRequest, ProviderResponse
from .validation import valid_secret


class CerebrasProvider(BaseProvider):

    name = "cerebras"

    def __init__(self):
        self.key = os.getenv("CEREBRAS_API_KEY")
        self.model = os.getenv(
            "CEREBRAS_MODEL",
            "llama-4-scout-17b-16e-instruct",
        )

    async def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "CEREBRAS_API_KEY not configured"
            )

        start_time = perf_counter()
        response = await http.post(
            "https://api.cerebras.ai/v1/chat/completions",
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
        )

        response.raise_for_status()

        data = response.json()

        return ProviderResponse(
            provider=self.name,
            model=request.model or self.model,
            content=data["choices"][0]["message"]["content"],
            raw=data,
            prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
            total_tokens=data.get("usage", {}).get("total_tokens", 0),
            latency=perf_counter() - start_time,
            provider_latency=perf_counter() - start_time,
            total_latency=perf_counter() - start_time,
        )

    def health(self):
        return valid_secret(self.key)

    def available(self):
        return valid_secret(self.key)

    def models(self):
        return [self.model]
