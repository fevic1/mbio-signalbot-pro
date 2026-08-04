from time import perf_counter
import os

from .base import BaseProvider
from .exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    TimeoutError,
)
from .transport import http
from .types import ProviderRequest, ProviderResponse
from .validation import valid_secret


class AnthropicProvider(BaseProvider):

    name = "anthropic"

    def __init__(self):
        self.key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv(
            "ANTHROPIC_MODEL_NAME",
            "claude-sonnet-4-20250514",
        )
        self.url = "https://api.anthropic.com/v1/messages"

    async def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "ANTHROPIC_API_KEY not configured"
            )

        system = None
        messages = []

        for m in request.messages:
            if m["role"] == "system":
                if system is None:
                    system = m["content"]
                continue

            messages.append(
                {
                    "role": m["role"],
                    "content": m["content"],
                }
            )

        payload = {
            "model": request.model or self.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }

        if system:
            payload["system"] = system

        start_time = perf_counter()

        try:
            r = await http.post(
                self.url,
                headers={
                    "x-api-key": self.key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
        except Exception as e:
            if e.__class__.__name__.lower().startswith("timeout"):
                raise TimeoutError(str(e))
            raise ProviderError(str(e))

        if r.status_code == 401:
            raise AuthenticationError(r.text)

        if r.status_code == 429:
            raise RateLimitError(r.text)

        if r.status_code >= 400:
            raise ProviderError(r.text)

        data = r.json()

        content = ""
        if data.get("content"):
            content = "".join(
                block.get("text", "")
                for block in data["content"]
                if block.get("type") == "text"
            )

        return ProviderResponse(
            provider=self.name,
            model=data.get("model", request.model or self.model),
            content=content,
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
