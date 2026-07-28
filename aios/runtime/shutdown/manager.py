from datetime import datetime, timezone


class RuntimeShutdownManager:

    def __init__(self, kernel):
        self._kernel = kernel
        self._shutdown = False
        self._history = []

    def register(self, component: str):
        self._history.append({
            "action": "registered",
            "component": component,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

    def shutdown(self):
        if self._shutdown:
            return False

        self._shutdown = True

        self._history.append({
            "action": "shutdown",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        return True

    def restart(self):
        self._shutdown = False

        self._history.append({
            "action": "restart",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        return True

    def is_shutdown(self):
        return self._shutdown

    def history(self):
        return tuple(self._history)

    def export(self):
        return {
            "shutdown": self._shutdown,
            "history": list(self._history),
        }
