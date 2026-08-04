import os

from .base import BaseProvider
from .exceptions import AuthenticationError
from .transport import http
from .types import ProviderRequest, ProviderResponse
from .validation import valid_secret


class GroqProvider(BaseProvider):

    name = "groq"

    def __init__(self):
        self.key = os.getenv("AIOS_GROQ_API_KEY")

        self.model = os.getenv(
            "AIOS_GROQ_MODEL",
            "llama-3.1-8b-instant",
        )

    async def chat(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        if not self.key:
            raise AuthenticationError(
                "AIOS_GROQ_API_KEY not configured"
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

        response = await http.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code >= 400:
            print("GROQ ERROR:", response.text, flush=True)

        response.raise_for_status()

        data = response.json()

        message = data["choices"][0]["message"]

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            # Tool-call responses may have no assistant text.
            content=message.get("content") or "",
            raw=data,
            prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
            total_tokens=data.get("usage", {}).get("total_tokens", 0),
        )

    def health(self):
        return valid_secret(self.key)

    def available(self):
        return valid_secret(self.key)

    def models(self):
        return [self.model]
