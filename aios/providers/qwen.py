import os

from .base import BaseProvider
from .exceptions import AuthenticationError
from .transport import http
from .types import ProviderRequest, ProviderResponse
from .validation import valid_secret


class QwenProvider(BaseProvider):

    name = "qwen"

    def __init__(self):
        self.key = os.getenv("AIOS_QWEN_API_KEY")
        self.model = os.getenv(
            "AIOS_QWEN_MODEL",
            "qwen3.7-plus",
        )
        self.base_url = os.getenv(
            "AIOS_QWEN_BASE_URL",
            "",
        ).rstrip("/")

    async def chat(self, request: ProviderRequest) -> ProviderResponse:
        if not self.key:
            raise AuthenticationError(
                "AIOS_QWEN_API_KEY not configured"
            )

        if not self.base_url:
            raise AuthenticationError(
                "AIOS_QWEN_BASE_URL not configured"
            )

        messages = []

        for message in request.messages:
            content = message.get("content")

            if content is None:
                content = ""
            elif not isinstance(content, (str, list)):
                content = str(content)

            item = {
                "role": message.get("role"),
                "content": content,
            }

            for key in ("tool_calls", "tool_call_id", "name"):
                if key in message:
                    item[key] = message[key]

            messages.append(item)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        thinking = os.getenv(
            "AIOS_QWEN_THINKING",
            "false",
        ).strip().lower()

        payload["enable_thinking"] = thinking in {
            "1",
            "true",
            "yes",
            "on",
        }

        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = "auto"

        response = await http.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code >= 400:
            print(
                "QWEN ERROR:",
                response.status_code,
                response.text[:500],
                flush=True,
            )

        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            content=message.get("content") or "",
            raw=data,
        )

    def health(self):
        return valid_secret(self.key) and bool(self.base_url)

    def available(self):
        return self.health()

    def models(self):
        return [self.model]
