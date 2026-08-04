from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass(slots=True)
class StageLatency:
    compiler: float = 0.0
    provider: float = 0.0
    tool: float = 0.0
    verification: float = 0.0
    total: float = 0.0


class ExecutionTimer:
    """
    Runtime latency tracker.

    Usage:

        timer = ExecutionTimer()
        timer.begin()

        timer.start("compiler")
        ...
        timer.stop("compiler")

        timer.start("verification")
        ...
        timer.stop("verification")

        timer.finish()

        print(timer.latency.total)
    """

    def __init__(self):
        self._marks: dict[str, float] = {}
        self._runtime_start: float | None = None
        self.latency = StageLatency()

    def begin(self) -> None:
        self._runtime_start = perf_counter()

    def start(self, stage: str) -> None:
        self._marks[stage] = perf_counter()

    def stop(self, stage: str) -> float:
        started = self._marks.pop(stage, None)

        if started is None:
            return 0.0

        elapsed = perf_counter() - started

        if stage == "compiler":
            self.latency.compiler = elapsed
        elif stage == "provider":
            self.latency.provider = elapsed
        elif stage == "tool":
            self.latency.tool = elapsed
        elif stage == "verification":
            self.latency.verification = elapsed

        return elapsed

    def finish(self) -> float:
        if self._runtime_start is None:
            self.latency.total = (
                self.latency.compiler
                + self.latency.provider
                + self.latency.tool
                + self.latency.verification
            )
        else:
            self.latency.total = perf_counter() - self._runtime_start

        return self.latency.total

    def reset(self) -> None:
        self._marks.clear()
        self._runtime_start = None
        self.latency = StageLatency()

    def snapshot(self) -> dict[str, float]:
        return {
            "compiler": self.latency.compiler,
            "provider": self.latency.provider,
            "tool": self.latency.tool,
            "verification": self.latency.verification,
            "total": self.latency.total,
        }
