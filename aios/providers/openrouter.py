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


class OpenRouterProvider(BaseProvider):

    name = "openrouter"

    def __init__(self):

        self.key = os.getenv("OPENROUTER_API_KEY")

        self.model = os.getenv(
            "OPENROUTER_MODEL_NAME",
            "openai/gpt-4.1-mini",
        )

        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, request: ProviderRequest) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "OPENROUTER_API_KEY not configured"
            )

        try:

            r = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv(
                        "OPENROUTER_SITE_URL",
                        "https://localhost",
                    ),
                    "X-Title": os.getenv(
                        "OPENROUTER_APP_NAME",
                        "AIOS",
                    ),
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

    def health(self) -> bool:
        return self.key is not None

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
