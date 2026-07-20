import os

from ..base import Provider
from ..registry import register

class GroqProvider(Provider):

    name="groq"

    def available(self):

        return bool(
            os.getenv("GROQ_API_KEY")
            or os.getenv("GROQ_API_KEY_1")
        )

    def models(self):

        return [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ]

    def health(self):

        return "healthy"

    def chat(self,messages,**kwargs):

        return {
            "provider":"groq",
            "status":"ready",
            "messages":messages
        }

register(GroqProvider())
