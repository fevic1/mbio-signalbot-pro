import os

from dataclasses import dataclass

from .protocol import (
    AIOSRequest,
    AIOSResponse,
)

from aios.runtime.telemetry.timer import ExecutionTimer
from aios.runtime.cost.pricing import calculate_cost
from aios.runtime.verification.engine import VerificationEngine
from aios.runtime.learning.engine import LearningEngine
from aios.runtime.provider_health.engine import ProviderHealthEngine
from aios.runtime.provider_router.engine import AdaptiveProviderRouter

from .adapters import (
    NativeProviderAdapter,
    adapter_registry,
)

from .context import (
    SemanticContextProcessor,
)


@dataclass(frozen=True, slots=True)
class _AdaptiveRoutePlan:
    """
    Minimal immutable plan view for AdaptiveProviderRouter.

    Replaces dynamic type() class generation.
    """

    metadata: dict


def _first_positive(*candidates):
    """
    Pure helper: returns the first candidate coercible to a float > 0.

    Deterministic precedence for telemetry sources.
    """
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            value = float(candidate)
        except (TypeError, ValueError):
            continue
        if value > 0.0:
            return value
    return 0.0


def _upstream_compiler_latency(constraints):
    """
    Pure helper: extracts compiler latency passed down by upstream
    stages (executor/proxy) via request constraints.
    """
    compiler_block = constraints.get("compiler")

    nested = None

    if isinstance(compiler_block, dict):
        nested = compiler_block.get("compiler_latency")

    return _first_positive(
        constraints.get("compiler_latency"),
        nested,
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
        timer.begin()

        timer.start("provider")

        provider_request = (
            adapter
            .translate_request(
                request
            )
        )

        provider_request.route = request.constraints.get(
            "provider_fallback_chain",
            (),
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

        # The gateway owns the verification stage: measure it here.
        timer.start("verification")

        verification = VerificationEngine().verify(response)

        timer.stop("verification")

        health = ProviderHealthEngine().update(
            provider=response.provider,
            success=verification.passed,
            latency=timer.latency.provider,
            cost=estimated_cost,
        )

        route_decision = AdaptiveProviderRouter().choose(
            execution_plan=_AdaptiveRoutePlan(
                metadata={
                    "provider_fallback_chain": response.route_metadata.get(
                        "provider_order",
                        [],
                    ),
                    "selected_provider": response.provider,
                }
            ),
            provider_health={
                response.provider: health,
            },
        )

        # Telemetry merge: each stage has exactly one source of truth.
        compiler_latency = _first_positive(
            _upstream_compiler_latency(request.constraints),
            getattr(response, "compiler_latency", 0.0),
        )

        provider_latency = _first_positive(
            timer.latency.provider,
            getattr(response, "latency", 0.0),
        )

        verification_latency = timer.latency.verification

        tool_latency = _first_positive(
            getattr(response, "tool_latency", 0.0),
        )

        # Total = upstream compile time + gateway wall-clock runtime.
        total_latency = compiler_latency + timer.finish()

        telemetry = {
            "compiler_latency": compiler_latency,
            "provider_latency": provider_latency,
            "tool_latency": tool_latency,
            "verification_latency": verification_latency,
            "total_latency": total_latency,
        }

        learning_record = LearningEngine().record(
            AIOSResponse(
                provider=response.provider,
                model=response.model,
                content=response.content,
                prompt_tokens=getattr(response, "prompt_tokens", 0),
                completion_tokens=getattr(response, "completion_tokens", 0),
                total_tokens=getattr(response, "total_tokens", 0),
                latency=getattr(response, "latency", timer.latency.provider),
                compiler_latency=telemetry["compiler_latency"],
                provider_latency=telemetry["provider_latency"],
                tool_latency=telemetry["tool_latency"],
                verification_latency=telemetry["verification_latency"],
                total_latency=telemetry["total_latency"],
                estimated_cost=estimated_cost,
                prompt_cost=prompt_cost,
                completion_cost=completion_cost,
                verification_score=verification.score,
                verification_passed=verification.passed,
                verification_report=verification.report,
                route_metadata=response.route_metadata,
                metadata={
                    "capability": request.capability,
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
            compiler_latency=telemetry["compiler_latency"],
            provider_latency=telemetry["provider_latency"],
            tool_latency=telemetry["tool_latency"],
            verification_latency=telemetry["verification_latency"],
            total_latency=telemetry["total_latency"],
            cost=getattr(response, "cost", estimated_cost),
            estimated_cost=estimated_cost,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            verification_score=verification.score,
            verification_passed=verification.passed,
            verification_report=verification.report,
            route_metadata={
                "provider_order": os.getenv(
                    "AIOS_PROVIDER_ORDER",
                    "",
                ).split(","),
                "selected_provider": response.provider,
                "selected_model": response.model,
                "provider_route_metadata": response.route_metadata,
            },
            metadata={
                "learning_record": learning_record,
                "provider_health": health,
                "adaptive_route": {
                    "provider": route_decision.provider,
                    "score": route_decision.score,
                },
                "capability": request.capability,
                "raw": response.raw,
            },
        )
