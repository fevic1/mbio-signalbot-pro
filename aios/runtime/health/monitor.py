
from datetime import datetime, timezone

from .models import RuntimeHealth


class RuntimeHealthMonitor:

    def __init__(self, kernel):
        self._kernel = kernel
        self._checks = {
            "kernel": kernel.status,
        }


    def register(self, name, check):
        self._checks[name] = check


    def check(self):

        results = {}

        healthy = True

        for name, check in self._checks.items():

            try:
                result = check()

                results[name] = result

                if isinstance(result, dict):
                    if not all(result.values()):
                        healthy = False

                elif not result:
                    healthy = False

            except Exception as exc:

                healthy = False

                results[name] = {
                    "error": str(exc)
                }


        return RuntimeHealth(
            status="ok" if healthy else "warning",
            details=results,
        )


    def healthy(self):

        return self.check().status == "ok"
