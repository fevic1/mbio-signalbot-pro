import os

from ..base import Provider
from ..registry import register

class CerebrasProvider(Provider):

    name="cerebras"

    def available(self):

        return bool(os.getenv("CEREBRAS_API_KEY"))

    def models(self):

        return ["llama"]

    def health(self):

        return "healthy"

    def chat(self,messages,**kwargs):

        return {
            "provider":"cerebras",
            "status":"ready"
        }

register(CerebrasProvider())
