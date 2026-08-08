#!/usr/bin/env python3

from datetime import UTC, datetime


class HealthManager:

    def __init__(self):
        self.checks = {}

    def register(self, name, check):
        self.checks[name] = check

    def unregister(self, name):
        self.checks.pop(name, None)

    def run(self):

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }

        for name, check in self.checks.items():

            try:
                result = check()

                if isinstance(result, dict):
                    report["checks"][name] = result
                    if result.get("status") != "healthy":
                        report["status"] = "degraded"
                else:
                    report["checks"][name] = {
                        "status": "healthy"
                    }

            except Exception as e:
                report["checks"][name] = {
                    "status": "failed",
                    "error": str(e)
                }
                report["status"] = "failed"

        return report


health = HealthManager()


if __name__ == "__main__":

    health.register(
        "runtime",
        lambda: {"status": "healthy"}
    )

    health.register(
        "memory",
        lambda: {"status": "healthy"}
    )

    print(health.run())
