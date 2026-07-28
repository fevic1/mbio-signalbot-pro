from dataclasses import dataclass, field

from aios.runtime.state import RuntimeState


@dataclass(slots=True)
class RuntimeStatus:
    state: RuntimeState = RuntimeState.CREATED
    started: bool = False
    services: int = 0
    agents: int = 0
    tasks: int = 0
    plugins: int = 0
    extensions: int = 0
    metadata: dict = field(default_factory=dict)

    def export(self):
        return {
            "state": self.state.value,
            "started": self.started,
            "services": self.services,
            "agents": self.agents,
            "tasks": self.tasks,
            "plugins": self.plugins,
            "extensions": self.extensions,
            "metadata": dict(self.metadata),
        }
