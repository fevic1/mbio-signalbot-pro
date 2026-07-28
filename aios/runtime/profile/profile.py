from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeProfile:
    name: str = "default"
    mode: str = "production"
    debug: bool = False
    metadata: dict = field(default_factory=dict)

    def export(self):
        return {
            "name": self.name,
            "mode": self.mode,
            "debug": self.debug,
            "metadata": dict(self.metadata),
        }
