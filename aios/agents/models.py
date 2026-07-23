from dataclasses import dataclass, field


@dataclass
class Agent:

    role: str

    capabilities: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
