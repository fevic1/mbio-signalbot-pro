from time import perf_counter
import os

from .base import BaseProvider
from .exceptions import AuthenticationError
from .transport import http
from .types import ProviderRequest, ProviderResponse
from .validation import valid_secret


class DeepSeekProvider(BaseProvider):

    name = "deepseek"

    def __init__(self):
        self.key = os.getenv("AIOS_DEEPSEEK_API_KEY")

        self.model = os.getenv(
            "AIOS_DEEPSEEK_MODEL",
            "deepseek-v4-flash",
        )

        self.base_url = os.getenv(
            "AIOS_DEEPSEEK_BASE_URL",
            "https://api.deepseek.com",
        ).rstrip("/")

    async def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "AIOS_DEEPSEEK_API_KEY not configured"
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

        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = "auto"

        start_time = perf_counter()
        response = await http.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code >= 400:
            print("DEEPSEEK ERROR:", response.text, flush=True)

        response.raise_for_status()

        data = response.json()

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            content=data["choices"][0]["message"]["content"] or "",
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
