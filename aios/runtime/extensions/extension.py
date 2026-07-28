from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeExtension:
    name: str
    enabled: bool = True
    metadata: dict = field(default_factory=dict)

    def initialize(self, kernel):
        pass

    def shutdown(self, kernel):
        pass
