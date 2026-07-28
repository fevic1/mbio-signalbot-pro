from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeEvent:
    name: str
    payload: object | None = None
    metadata: dict = field(default_factory=dict)
