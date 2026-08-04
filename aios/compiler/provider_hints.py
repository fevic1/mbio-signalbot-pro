from .models import ProviderHints


class ProviderHintsBuilder:

    def build(
        self,
        capability: str,
    ) -> ProviderHints:

        reasoning = capability in {
            "research",
            "planning",
            "analysis",
        }

        return ProviderHints(
            prefers_reasoning=reasoning,
            prefers_speed=not reasoning,
        )
