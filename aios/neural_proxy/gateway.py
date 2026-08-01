from .protocol import (
    AIOSRequest,
    AIOSResponse,
)

from .adapters import (
    NativeProviderAdapter,
    adapter_registry,
)

from .context import (
    SemanticContextProcessor,
)


class NeuralProxyGateway:


    def __init__(
        self,
        router,
        provider_chat,
        adapter=None,
        event_bus=None,
    ):

        self.router = router
        self.provider_chat = provider_chat
        self.adapter = adapter
        self.event_bus = event_bus
        self.context_processor = SemanticContextProcessor()


    async def execute(
        self,
        request: AIOSRequest,
    ):

        request = self.context_processor.process(
            request
        )

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

            request.constraints[
                "provider"
            ] = model.provider


        adapter = self.adapter

        if adapter is None:

            if model:

                adapter = (
                    adapter_registry.get(
                        model.provider
                    )
                    or NativeProviderAdapter()
                )

            else:

                adapter = NativeProviderAdapter()


        provider_request = (
            adapter
            .translate_request(
                request
            )
        )


        response = await self.provider_chat(
            provider_request
        )


        if self.event_bus:

            from aios.events.models import AIOSDomainEvent

            self.event_bus.publish(
                AIOSDomainEvent(
                    "model_execution.completed",
                    source="neural_proxy",
                    payload={
                        "provider": response.provider,
                        "model": response.model,
                        "capability": request.capability,
                        "success": True,
                    },
                )
            )


        return AIOSResponse(
            provider=response.provider,
            model=response.model,
            content=response.content,
            metadata={
                "capability": request.capability,
                "raw": response.raw,
            },
        )
