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


        timer = ExecutionTimer()
        timer.start("provider")

        provider_request = (
            adapter
            .translate_request(
                request
            )
        )

        provider_request.route = request.constraints.get(
            "provider_fallback_chain",
            ()
        )

        provider_request.selected_provider = request.constraints.get(
            "provider"
        )

        provider_request.selected_model = request.constraints.get(
            "model"
        )


        from aios.events.models import AIOSDomainEvent

        try:

            route = tuple(
                getattr(
                    provider_request,
                    "route",
                    (),
                )
            )

            if not route:
                route = (
                    getattr(
                        provider_request,
                        "selected_provider",
                        None,
                    ),
                )

            last_error = None

            for provider in route:

                if provider:
                    provider_request.provider = provider

                try:
                    response = await self.provider_chat(
                        provider_request,
                        event_bus=self.event_bus,
                        capability=request.capability,
                    )
                    break

                except Exception as error:
                    last_error = error

            else:
                raise last_error

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

        timer.stop("provider")

        prompt_cost, completion_cost, estimated_cost = calculate_cost(
            response.model,
            getattr(response, "prompt_tokens", 0),
            getattr(response, "completion_tokens", 0),
        )

        verification = VerificationEngine().verify(response)

        learning_record = LearningEngine().record(
            AIOSResponse(
                provider=response.provider,
                model=response.model,
                content=response.content,
                prompt_tokens=getattr(response,"prompt_tokens",0),
                completion_tokens=getattr(response,"completion_tokens",0),
                total_tokens=getattr(response,"total_tokens",0),
                latency=getattr(response,"latency",timer.latency.provider),
                compiler_latency=0.0,
                provider_latency=timer.latency.provider,
                tool_latency=0.0,
                verification_latency=0.0,
                total_latency=timer.latency.provider,
                estimated_cost=estimated_cost,
                prompt_cost=prompt_cost,
                completion_cost=completion_cost,
                verification_score=verification.score,
                verification_passed=verification.passed,
                verification_report=verification.report,
                metadata={
                "learning_record": learning_record,
                    "capability":request.capability,
                },
            )
        )

        return AIOSResponse(
            provider=response.provider,
            model=response.model,
            content=response.content,
            prompt_tokens=getattr(response, "prompt_tokens", 0),
            completion_tokens=getattr(response, "completion_tokens", 0),
            total_tokens=getattr(response, "total_tokens", 0),
            latency=getattr(response, "latency", timer.latency.provider),
            compiler_latency=getattr(response, "compiler_latency", 0.0),
            provider_latency=getattr(response, "provider_latency", timer.latency.provider),
            tool_latency=getattr(response, "tool_latency", 0.0),
            verification_latency=getattr(response, "verification_latency", 0.0),
            total_latency=getattr(response, "total_latency", timer.latency.provider),
            cost=getattr(response, "cost", estimated_cost),
            estimated_cost=estimated_cost,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            verification_score=verification.score,
            verification_passed=verification.passed,
            verification_report=verification.report,
            route_metadata={
                "provider_order": __import__("os").getenv(
                    "AIOS_PROVIDER_ORDER",
                    "",
                ).split(","),
                "selected_provider": response.provider,
                "selected_model": response.model,
            },
            metadata={
                "learning_record": learning_record,
                "capability": request.capability,
                "raw": response.raw,
            },
        )
