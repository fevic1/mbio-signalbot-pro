from datetime import datetime, timezone


class RuntimeDiagnostics:

    def __init__(self, kernel):
        self._kernel = kernel

    def inspect(self):
        return {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "identity": self._kernel.identity.export(),
            "platform": self._kernel.platform.export(),
            "capabilities": self._kernel.capabilities.export(),
            "features": self._kernel.features.export(),
            "services": self._kernel.services.export(),
            "resources": self._kernel.resources.export(),
            "modules": self._kernel.modules.export(),
            "extensions": self._kernel.extensions.export(),
            "providers": self._kernel.providers.export(),
            "drivers": self._kernel.drivers.export(),
            "adapters": self._kernel.adapters.export(),
            "connectors": self._kernel.connectors.export(),
        }

    def healthy(self):
        monitor = getattr(
            self._kernel,
            "health_monitor",
            None,
        )

        if monitor is None:
            return False

        return monitor.healthy()
