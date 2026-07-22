from dataclasses import dataclass, field
from time import time


@dataclass
class ProviderMetrics:
    requests: int = 0
    successes: int = 0
    failures: int = 0
    retries: int = 0
    total_latency: float = 0.0

    def latency(self):
        if self.successes == 0:
            return 0.0
        return self.total_latency / self.successes


class MetricsRegistry:

    def __init__(self):
        self.metrics = {}

    def get(self, provider):

        if provider not in self.metrics:
            self.metrics[provider] = ProviderMetrics()

        return self.metrics[provider]

    def record_success(self, provider, latency):

        m = self.get(provider)
        m.requests += 1
        m.successes += 1
        m.total_latency += latency

    def record_failure(self, provider):

        m = self.get(provider)
        m.requests += 1
        m.failures += 1

    def record_retry(self, provider):

        self.get(provider).retries += 1


metrics = MetricsRegistry()
