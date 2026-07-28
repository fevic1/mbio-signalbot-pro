from dataclasses import dataclass, field

from aios.execution.graph import ExecutionGraph


@dataclass(slots=True)
class Workflow:
    id: str
    graph: ExecutionGraph = field(default_factory=ExecutionGraph)
    metadata: dict = field(default_factory=dict)
