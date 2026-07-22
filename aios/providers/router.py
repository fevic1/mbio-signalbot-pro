from time import perf_counter

from .metrics import metrics
from .registry import registry
from .scoring import score


ORDER = [
    "groq",
    "cerebras",
    "openrouter",
    "anthropic",
]


def chat(request, preferred="groq"):

    providers = sorted(
        [
            provider
            for provider in (
                registry.get(name)
                for name in ORDER
            )
            if provider is not None
        ],
        key=score,
        reverse=True,
    )

    last_error = None

    for provider in providers:

        name = provider.name

        if not provider.available():
            continue

        start = perf_counter()

        try:
            response = provider.chat(request)

            metrics.record_success(
                name,
                perf_counter() - start,
            )

            return response

        except Exception as exc:

            metrics.record_failure(name)
            metrics.record_retry(name)

            last_error = exc
            continue

    raise last_error
