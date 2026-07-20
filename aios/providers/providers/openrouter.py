import os

from ..base import Provider
from ..registry import register

class OpenRouterProvider(Provider):

    name="openrouter"

    def available(self):

        return bool(os.getenv("OPENROUTER_API_KEY"))

    def models(self):

        return ["auto"]

    def health(self):

        return "healthy"

    def chat(self,messages,**kwargs):

        return {
            "provider":"openrouter",
            "status":"ready"
        }

register(OpenRouterProvider())
