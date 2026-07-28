#!/usr/bin/env python3

from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt, **kwargs):
        pass


class LLMService:

    def __init__(self):
        self.providers = {}
        self.default = None

    def register(self, name, provider):
        self.providers[name] = provider

        if self.default is None:
            self.default = name

    def set_default(self, name):
        if name not in self.providers:
            raise KeyError(name)
        self.default = name

    def available(self):
        return sorted(self.providers.keys())

    def generate(self, prompt, provider=None, **kwargs):

        provider = provider or self.default

        if provider not in self.providers:
            raise KeyError(provider)

        return self.providers[provider].generate(
            prompt,
            **kwargs
        )


class MockProvider(LLMProvider):

    def generate(self, prompt, **kwargs):
        return {
            "provider": "mock",
            "response": f"Mock response: {prompt}"
        }


llm = LLMService()


if __name__ == "__main__":

    llm.register("mock", MockProvider())

    print(llm.available())

    print(
        llm.generate(
            "Hello AIOS"
        )
    )
