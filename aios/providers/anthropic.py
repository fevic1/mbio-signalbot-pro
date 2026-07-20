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


class AnthropicProvider(BaseProvider):

    name = "anthropic"

    def __init__(self):

        self.key = os.getenv("ANTHROPIC_API_KEY")

        self.model = os.getenv(
            "ANTHROPIC_MODEL_NAME",
            "claude-sonnet-4-20250514",
        )

        self.url = "https://api.anthropic.com/v1/messages"

    def chat(self, request: ProviderRequest) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError("ANTHROPIC_API_KEY not configured")

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

        try:

            r = requests.post(
                self.url,
                headers={
                    "x-api-key": self.key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
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
        )

    def health(self) -> bool:
        return self.key is not None

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
