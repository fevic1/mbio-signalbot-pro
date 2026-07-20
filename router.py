from .registry import registry

ORDER = [
    "groq",
    "openrouter",
    "cerebras",
    "anthropic",
]


def chat(request, preferred="groq"):

    providers = [preferred] + [p for p in ORDER if p != preferred]

    last_error = None

    for name in providers:

        provider = registry.providers.get(name)

        if provider is None:
            continue

        try:
            return provider.chat(request)

        except Exception as e:
            last_error = e

    raise last_error
