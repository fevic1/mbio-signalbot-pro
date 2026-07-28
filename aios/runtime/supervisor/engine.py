
from datetime import datetime, timezone


class Supervisor:

    def __init__(self):
        self.components = {}
        self.events = []

    def register(self, name, component):
        self.components[name] = component

    def check(self):
        results = {}

        for name, component in self.components.items():
            healthy = True

            health = getattr(
                component,
                "healthy",
                None,
            )

            if callable(health):
                healthy = bool(
                    health()
                )

            results[name] = healthy

        return results

    def recover(self, name):
        component = self.components.get(name)

        if component is None:
            return False

        restart = getattr(
            component,
            "restart",
            None,
        )

        if callable(restart):
            restart()

        self.events.append({
            "component": name,
            "action": "recovered",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        return True

    def history(self):
        return tuple(self.events)
