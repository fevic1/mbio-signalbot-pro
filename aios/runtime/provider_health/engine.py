from dataclasses import dataclass, field


@dataclass(slots=True)
class ProviderStats:
    requests: int = 0
    successes: int = 0
    failures: int = 0
    total_latency: float = 0.0
    total_cost: float = 0.0


class ProviderHealthEngine:

    def __init__(self):
        self.providers: dict[str, ProviderStats] = {}

    def update(
        self,
        provider: str,
        success: bool,
        latency: float,
        cost: float,
    ):
        stats = self.providers.setdefault(
            provider,
            ProviderStats(),
        )

        stats.requests += 1

        if success:
            stats.successes += 1
        else:
            stats.failures += 1

        stats.total_latency += latency
        stats.total_cost += cost

        return {
            "requests": stats.requests,
            "success_rate":
                stats.successes / stats.requests,
            "failure_rate":
                stats.failures / stats.requests,
            "average_latency":
                stats.total_latency / stats.requests,
            "average_cost":
                stats.total_cost / stats.requests,
        }
