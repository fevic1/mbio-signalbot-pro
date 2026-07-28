from dataclasses import dataclass, field
import uuid


@dataclass(slots=True)
class RuntimeIdentity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "runtime"
    instance: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def export(self):
        return {
            "id": self.id,
            "name": self.name,
            "instance": self.instance,
        }
