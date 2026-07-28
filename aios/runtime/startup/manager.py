from datetime import datetime, timezone


class RuntimeStartupManager:

    def __init__(self, kernel):
        self._kernel = kernel
        self._started = False
        self._history = []

    def register(self, component: str):
        self._history.append({
            "action": "registered",
            "component": component,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

    def start(self):
        if self._started:
            return False

        self._started = True

        self._history.append({
            "action": "startup",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        return True

    def stop(self):
        self._started = False

        self._history.append({
            "action": "stopped",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })

        return True

    def running(self):
        return self._started

    def history(self):
        return tuple(self._history)

    def export(self):
        return {
            "running": self._started,
            "history": list(self._history),
        }
