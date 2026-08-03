import asyncio
from time import perf_counter

from .circuit import circuit
from .metrics import metrics
from .pool import provider_pool
from .retry import retry
from .types import ProviderRequest
from aios.events.models import AIOSDomainEvent


async def chat(
    request: ProviderRequest,
    event_bus=None,
    capability=None,
):

    last_error = None

    ranked = provider_pool.ranked()

    if request.provider:
        ranked = [
            provider
            for provider in ranked
            if provider.name == request.provider
        ]

    for provider in ranked:

        name = provider.name

        if not circuit.allow(name):
            continue

        if not provider.available():
            continue

        start = perf_counter()

        try:
            response = await retry(
                lambda: asyncio.wait_for(
                    provider.chat(request),
                    timeout=60,
                ),
                retries=1,
                delay=0.25,
            )

            latency = perf_counter() - start

            metrics.record_success(
                name,
                latency,
            )

            circuit.success(name)

            if event_bus:
                event_bus.publish(
                    AIOSDomainEvent(
                        "provider_execution.completed",
                        source="provider_router",
                        payload={
                            "provider": name,
                            "capability": capability,
                            "latency_ms": latency * 1000,
                            "success": True,
                        },
                    )
                )

            return response

        except Exception as exc:
            metrics.record_failure(name)
            metrics.record_retry(name)

            circuit.failure(name)

            if event_bus:
                event_bus.publish(
                    AIOSDomainEvent(
                        "provider_execution.failed",
                        source="provider_router",
                        payload={
                            "provider": name,
                            "capability": capability,
                            "error": str(exc),
                            "success": False,
                        },
                    )
                )

            last_error = exc

    if last_error:
        return {'success': False, 'reason': str(
            f"Provider failures: {last_error}"
        ) from last_error

    raise RuntimeError(
        "No provider available"
    )
