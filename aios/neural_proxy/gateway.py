import os

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

        # AIOS_PROVIDER_ORDER controls provider selection and fallback.
        # The legacy model router otherwise pins requests to Groq.
        if os.getenv("AIOS_PROVIDER_ORDER"):
            model = None
            request.constraints.pop("model", None)
            request.constraints.pop("provider", None)
        else:
            model = self.router.select(
                request.capability,
                request.constraints.get(
                    "allowed_models"
                ),
            )

            if model:
                request.constraints["model"] = model.name
                request.constraints["provider"] = model.provider


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


        from aios.events.models import AIOSDomainEvent

        try:
            response = await self.provider_chat(
                provider_request,
                event_bus=self.event_bus,
                capability=request.capability,
            )
        except Exception as error:
            if self.event_bus:
                self.event_bus.publish(
                    AIOSDomainEvent(
                        "model_execution.failed",
                        source="neural_proxy",
                        payload={
                            "capability": request.capability,
                            "error": str(error),
                            "success": False,
                        },
                    )
                )
            raise

        if self.event_bus:
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
