from .models import OperationEvent


class HealthMonitor:


    def check(
        self,
        system,
    ):

        health = getattr(
            system,
            "health",
            "unknown",
        )


        status = (
            "healthy"
            if health == "healthy"
            else "warning"
        )


        return OperationEvent(
            action="health.check",
            status=status,
            details={
                "system": system.name,
                "health": health,
            },
        )
