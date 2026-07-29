from datetime import datetime, timezone

from aios.events.models import AIOSDomainEvent


class ExecutionEventPublisher:


    def __init__(
        self,
        event_bus=None,
    ):

        self.event_bus = event_bus



    def publish_started(
        self,
        agent,
        task,
    ):

        return self._publish(
            "execution.started",
            agent,
            task,
            {
                "status": "started",
            },
        )



    def publish_completed(
        self,
        agent,
        task,
        result,
    ):

        return self._publish(
            "execution.completed",
            agent,
            task,
            {
                "status": "completed",
                "result": result,
                "governance": (
                    result.get("metadata", {})
                    .get("governance")
                ),
            },
        )



    def publish_failed(
        self,
        agent,
        task,
        error,
    ):

        return self._publish(
            "execution.failed",
            agent,
            task,
            {
                "status": "failed",
                "error": str(error),
            },
        )



    def _publish(
        self,
        event_type,
        agent,
        task,
        payload,
    ):

        event = AIOSDomainEvent(
            event_type,
            source="aios_execution",
            payload={
                "agent": (
                    agent.name
                    if hasattr(agent, "name")
                    else str(agent)
                ),
                "role": (
                    agent.role
                    if hasattr(agent, "role")
                    else ""
                ),
                "task": task,
                "timestamp": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
                **payload,
            },
        )


        if self.event_bus:

            self.event_bus.publish(
                event
            )


        return event
