from dataclasses import dataclass, field


@dataclass(slots=True)
class MemoryDocument:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)
