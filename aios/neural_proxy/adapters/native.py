from aios.providers.types import (
    ProviderRequest,
)

from aios.neural_proxy.protocol import (
    AIOSRequest,
)


class NativeProviderAdapter:


    def translate_request(
        self,
        request: AIOSRequest,
    ):

        return ProviderRequest(
            messages=request.messages,
            model=request.constraints.get(
                "model"
            ),
            temperature=request.constraints.get(
                "temperature",
                0.2,
            ),
            max_tokens=request.constraints.get(
                "max_tokens",
                2048,
            ),
        )


    def translate_response(
        self,
        response,
    ):

        return {
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
            "raw": response.raw,
        }
