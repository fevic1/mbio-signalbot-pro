from .manager import provider_manager


DEFAULT_MODELS = {
    "groq": "llama-3.1-8b-instant",
    "cerebras": "llama-4-scout-17b-16e-instruct",
    "openrouter": "openai/gpt-oss-20b:free",
    "anthropic": "claude-3-5-sonnet-latest",
}


class ModelRouter:

    def model(self, provider_name: str) -> str:
        provider = provider_manager.provider(provider_name)

        if provider is None:
            raise RuntimeError(f"Unknown provider: {provider_name}")

        models = provider.models()

        if models:
            return models[0]

        return DEFAULT_MODELS[provider_name]

    def provider(self):
        best = provider_manager.best()

        if best is None:
            raise RuntimeError("No provider available.")

        return best.name

    def select(self):
        provider = self.provider()

        return provider, self.model(provider)


model_router = ModelRouter()
