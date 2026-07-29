from dataclasses import dataclass


@dataclass
class HealthResult:
    status: str
    details: dict

    def get(self, key, default=None):
        return getattr(self, key, default)


class SystemHealth:

    def __init__(self, checks):
        self.checks = checks


    def check(self):

        results = [
            check()
            for check in self.checks
        ]

        healthy = all(
            item.get(
                "passed",
                False
            )
            for item in results
        )

        return HealthResult(
            status="ok" if healthy else "warning",
            details={
                "checks": results,
            },
        )
