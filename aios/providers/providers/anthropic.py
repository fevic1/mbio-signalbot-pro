import os

from ..base import Provider
from ..registry import register

class AnthropicProvider(Provider):

    name="anthropic"

    def available(self):

        return bool(os.getenv("ANTHROPIC_API_KEY"))

    def models(self):

        return ["claude"]

    def health(self):

        return "healthy"

    def chat(self,messages,**kwargs):

        return {
            "provider":"anthropic",
            "status":"ready"
        }

register(AnthropicProvider())

