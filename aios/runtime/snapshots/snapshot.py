from datetime import datetime, timezone


class RuntimeSnapshot:

    def __init__(self, kernel):
        self._kernel = kernel

    def create(self):
        return {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "state": self._kernel.state.value,
            "version": self._kernel.version.string,
            "services": sorted(
                self._kernel.services()
            ),
            "status": self._kernel.status.export(),
            "metrics": self._kernel.metrics.export(),
            "identity": self._kernel.identity.export(),
        }

    def state(self):
        return self.create()
