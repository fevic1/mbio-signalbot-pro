from dataclasses import dataclass


@dataclass(slots=True)
class RouteDecision:
    provider: str
    score: float


class AdaptiveProviderRouter:

    def choose(
        self,
        execution_plan,
        provider_health,
    ):
        route = execution_plan.metadata.get(
            "provider_fallback_chain",
            ()
        )

        if not route:
            raise RuntimeError(
                "No provider route available."
            )

        scores = {}

        for index, provider in enumerate(route):

            stats = provider_health.get(
                provider,
                {}
            )

            success = stats.get(
                "success_rate",
                1.0,
            )

            latency = stats.get(
                "average_latency",
                0.0,
            )

            cost = stats.get(
                "average_cost",
                0.0,
            )

            score = (
                success * 100
                - latency * 5
                - cost * 100
                - index
            )

            scores[provider] = score

        winner = max(
            scores,
            key=scores.get,
        )

        return RouteDecision(
            provider=winner,
            score=scores[winner],
        )
