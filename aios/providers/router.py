from time import perf_counter

from .circuit import circuit
from .metrics import metrics
from .pool import provider_pool
from .types import ProviderRequest


async def chat(request: ProviderRequest):

    last_error = None

    for provider in provider_pool.ranked():

        name = provider.name

        if not circuit.allow(name):
            continue

        if not provider.available():
            continue

        start = perf_counter()

        try:
            response = await provider.chat(request)

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
        raise last_error

    raise RuntimeError(
        "No provider available"
    )
