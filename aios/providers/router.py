from .registry import registry


ORDER = [
    "groq",
    "openrouter",
    "cerebras",
    "anthropic",
]


def chat(request, preferred="groq"):
    """
    Route request through available AI providers.
    Uses preferred provider first.
    Falls back automatically.
    """

    providers = [preferred] + [
        p for p in ORDER if p != preferred
    ]

    last_error = None

    for name in providers:

        provider = registry.get(name)

        if provider is None:
            continue

        # Skip providers without API keys
        if hasattr(provider, "available"):
            if not provider.available():
                continue

        try:
            return provider.chat(request)

        except Exception as e:
            last_error = e
            continue

    if last_error:
        raise last_error

    raise RuntimeError("No AI providers available")
