from .health import HealthStatus, HealthState


class Supervisor:

    def __init__(self):
        self._components: dict[str, object] = {}
        self._health: dict[str, HealthStatus] = {}

    def register(self, name: str, component):
        self._components[name] = component
        self._health[name] = HealthStatus(
            component=name,
            state=HealthState.UNKNOWN,
        )
        return component

    def unregister(self, name: str):
        self._health.pop(name, None)
        return self._components.pop(name, None)

    def component(self, name: str):
        return self._components[name]

    def status(self, name: str):
        return self._health[name]

    def update(self, name: str, state: HealthState, message: str = ""):
        status = self._health[name]
        status.state = state
        status.message = message
        return status

    def healthy(self):
        return [
            s
            for s in self._health.values()
            if s.state is HealthState.HEALTHY
        ]

    def failed(self):
        return [
            s
            for s in self._health.values()
            if s.state is HealthState.FAILED
        ]

    def __contains__(self, name):
        return name in self._components

    def __len__(self):
        return len(self._components)
