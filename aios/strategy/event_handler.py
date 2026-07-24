from datetime import datetime, timezone

from .workflow import StrategyWorkflow


class StrategyEventHandler:

    def __init__(
        self,
        workflow=None,
        event_bus=None,
    ):

        self.workflow = (
            workflow
            or StrategyWorkflow()
        )

        self.event_bus = event_bus


    def handle(
        self,
        event: dict,
    ):

        if event.get(
            "event_type"
        ) != "strategy.evaluation.requested":
            return None


        payload = event.get(
            "payload",
            {}
        )


        result = self.workflow.evaluate_version(
            strategy=payload.get(
                "strategy"
            ),
            current_version=payload.get(
                "current_version"
            ),
            candidate_version=payload.get(
                "candidate_version"
            ),
            current_metrics=payload.get(
                "current_metrics",
                {},
            ),
            candidate_metrics=payload.get(
                "candidate_metrics",
                {},
            ),
        )


        completed = {
            "event_type": "strategy.evaluation.completed",
            "source": "aios_strategy",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "payload": result,
        }


        if self.event_bus:

            self.event_bus.publish(
                completed
            )


        return completed
