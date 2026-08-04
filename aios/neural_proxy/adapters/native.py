from aios.providers.types import (
    ProviderRequest,
)

from aios.neural_proxy.protocol import (
    AIOSRequest,
    AIOSResponse,
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
            provider=request.constraints.get(
                "provider"
            ),
            temperature=request.constraints.get(
                "temperature",
                0.2,
            ),
            max_tokens=request.constraints.get(
                "max_tokens",
                2048,
            ),
            tools=request.tools,
            compiler=request.constraints.get(
                "compiler",
                {},
            ),
            provider_hints=request.constraints.get(
                "provider_hints",
                {},
            ),
            token_budget=request.constraints.get(
                "token_budget",
                {},
            ),
            execution_evidence=request.constraints.get(
                "execution_evidence",
                {},
            ),
        )


    def translate_response(
        self,
        response,
    ):

        return AIOSResponse(
            provider=response.provider,
            model=response.model,
            content=response.content,
            metadata={
                "raw": response.raw,
            },
        )
