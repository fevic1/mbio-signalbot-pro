from dataclasses import dataclass, field


@dataclass
class MemoryQuery:

    text: str

    layers: list[str] = field(
        default_factory=list
    )

    limit: int = 10

    include_graph: bool = True

    include_context: bool = True
