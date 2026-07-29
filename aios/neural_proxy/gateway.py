from .protocol import (
    AIOSRequest,
    AIOSResponse,
)

from .adapters import (
    NativeProviderAdapter,
)


class NeuralProxyGateway:


    def __init__(
        self,
        router,
        provider_chat,
        adapter=None,
    ):

        self.router = router
        self.provider_chat = provider_chat
        self.adapter = (
            adapter
            or NativeProviderAdapter()
        )


    async def execute(
        self,
        request: AIOSRequest,
    ):

        model = self.router.select(
            request.capability,
            request.constraints.get(
                "allowed_models"
            ),
        )


        if model:

            request.constraints[
                "model"
            ] = model.name


        provider_request = (
            self.adapter
            .translate_request(
                request
            )
        )


        response = await self.provider_chat(
            provider_request
        )


        return AIOSResponse(
            provider=response.provider,
            model=response.model,
            content=response.content,
            metadata={
                "capability":
                    request.capability,
            },
        )
