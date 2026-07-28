from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutionNode:
    id: str
    payload: object | None = None
    dependencies: set[str] = field(default_factory=set)
    dependents: set[str] = field(default_factory=set)
