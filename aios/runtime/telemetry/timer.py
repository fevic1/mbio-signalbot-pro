from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter


@dataclass(slots=True)
class StageLatency:
    compiler: float = 0.0
    planner: float = 0.0
    memory: float = 0.0
    tools: float = 0.0
    provider: float = 0.0
    verification: float = 0.0
    learning: float = 0.0
    total: float = 0.0


@dataclass(slots=True)
class ExecutionTimer:
    _marks: dict[str, float] = field(default_factory=dict)
    latency: StageLatency = field(default_factory=StageLatency)

    def start(self, stage: str):
        self._marks[stage] = perf_counter()

    def stop(self, stage: str):
        start = self._marks.pop(stage, None)
        if start is None:
            return 0.0
        elapsed = perf_counter() - start
        setattr(self.latency, stage, elapsed)
        return elapsed

    def begin(self):
        self.start("total")

    def finish(self):
        self.stop("total")
        return self.latency
