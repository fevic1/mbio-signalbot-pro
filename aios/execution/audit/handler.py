from datetime import datetime, timezone


class ExecutionAuditHandler:

    def __init__(
        self,
        event_bus,
        runtime_audit,
    ):

        self.runtime_audit = runtime_audit

        event_bus.subscribe(
            "execution.completed",
            self.handle,
        )


    def handle(
        self,
        event,
    ):

        payload = event.payload

        result = payload.get(
            "result",
            {},
        )

        governance = (
            result
            .get("metadata", {})
            .get("governance", {})
        )

        approved = (
            bool(governance.get("approval_id"))
            and governance.get("status") == "approved"
        )

        return self.runtime_audit.record(
            action="execution.completed",
            actor=payload.get(
                "agent",
                "unknown",
            ),
            metadata={
                "governance": governance,
                "approved": approved,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        )
