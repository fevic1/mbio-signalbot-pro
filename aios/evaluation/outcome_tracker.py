from datetime import datetime, timezone
import uuid


class OutcomeTracker:


    def __init__(self):

        self.outcomes = []



    def record(
        self,
        change_id,
        metrics_before,
        metrics_after,
    ):

        outcome = {

            "outcome_id":
                str(uuid.uuid4()),

            "change_id":
                change_id,

            "metrics_before":
                metrics_before,

            "metrics_after":
                metrics_after,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        self.outcomes.append(
            outcome
        )


        return outcome



    def history(self):

        return self.outcomes
