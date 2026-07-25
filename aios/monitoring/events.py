from datetime import datetime, timezone


class MonitoringEvents:


    def __init__(
        self,
        metrics,
    ):

        self.metrics = metrics



    def record(
        self,
        event,
    ):

        self.metrics.increment(
            event
        )

        return {

            "event":
                event,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }
