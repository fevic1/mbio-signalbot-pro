from dataclasses import dataclass


@dataclass
class CircuitBreaker:

    max_retries: int = 3
    max_runtime_seconds: int = 300

    retries: int = 0
    tripped: bool = False

    def check(self):
        if self.tripped:
            raise RuntimeError(
                "Circuit breaker active"
            )

        if self.retries >= self.max_retries:
            self.trip()

        return True

    def record_retry(self):
        self.retries += 1

        if self.retries >= self.max_retries:
            self.trip()

    def trip(self):
        self.tripped = True
