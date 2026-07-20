import os

import requests

from .base import BaseProvider
from .types import ProviderRequest, ProviderResponse
from .exceptions import AuthenticationError


class GroqProvider(BaseProvider):

    name = "groq"

    def __init__(self):

        self.key = (
            os.getenv("GROQ_API_KEY")
            or os.getenv("GROQ_API_KEY_1")
            or os.getenv("GROQ_API_KEY_2")
            or os.getenv("GROQ_API_KEY_3")
        )

        self.model = os.getenv(
            "GROQ_MODEL_NAME",
            "llama-3.1-8b-instant",
        )

    def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "GROQ_API_KEY not configured"
            )

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
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

        response.raise_for_status()

        data = response.json()

        return ProviderResponse(
            provider=self.name,
            model=request.model or self.model,
            content=data["choices"][0]["message"]["content"],
            raw=data,
        )

    def health(self) -> bool:
        return self.key is not None

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
