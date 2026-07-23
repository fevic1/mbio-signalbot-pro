from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CapabilityHealth:

    capability: str

    executions: int = 0

    successes: int = 0

    failures: int = 0

    total_latency: float = 0

    total_cost: float = 0

    last_execution: str | None = None


    def record_success(
        self,
        latency=0,
        cost=0,
    ):

        self.executions += 1
        self.successes += 1

        self.total_latency += latency
        self.total_cost += cost

        self.last_execution = (
            datetime.utcnow()
            .isoformat()
        )


    def record_failure(self):

        self.executions += 1
        self.failures += 1

        self.last_execution = (
            datetime.utcnow()
            .isoformat()
        )


    @property
    def success_rate(self):

        if self.executions == 0:
            return 0

        return (
            self.successes /
            self.executions
        )


    @property
    def average_latency(self):

        if self.successes == 0:
            return 0

        return (
            self.total_latency /
            self.successes
        )
