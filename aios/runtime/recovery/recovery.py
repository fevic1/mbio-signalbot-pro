from datetime import datetime, timezone


class RuntimeRecovery:

    def __init__(self, kernel):
        self._kernel = kernel
        self._attempts = []

    def record(self, component: str, error: str):
        event = {
            "component": component,
            "error": error,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._attempts.append(event)
        return event

    def attempts(self):
        return tuple(self._attempts)

    def recover(self, component: str):
        service = self._kernel.services().get(component)

        if service is None:
            return False

        restart = getattr(service, "restart", None)

        if callable(restart):
            restart()
            return True

        return False

    def clear(self):
        self._attempts.clear()

    def __len__(self):
        return len(self._attempts)
