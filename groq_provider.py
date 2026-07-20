import os

import requests

from .base import BaseProvider
from .types import ProviderResponse


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

    def chat(self, request):

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}"
            },
            json={
                "model": self.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
            timeout=60,
        )

        data = r.json()

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            content=data["choices"][0]["message"]["content"],
            raw=data,
        )

    def health(self):
        return self.key is not None

    def available(self) -> bool:
        return self.key is not None

    def models(self) -> list[str]:
        return [self.model]
