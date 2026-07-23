import asyncio
from time import perf_counter

from .circuit import circuit
from .metrics import metrics
from .pool import provider_pool
from .retry import retry
from .types import ProviderRequest


async def chat(request: ProviderRequest):

    last_error = None

    ranked = provider_pool.ranked()

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
                retries=3,
                delay=1.0,
            )

            latency = perf_counter() - start

            metrics.record_success(
                name,
                latency,
            )

            circuit.success(name)

            return response

        except Exception as exc:
            metrics.record_failure(name)
            metrics.record_retry(name)

            circuit.failure(name)

            last_error = exc

    if last_error:
        raise RuntimeError(
            f"Provider failures: {last_error}"
        ) from last_error

    raise RuntimeError(
        "No provider available"
    )
