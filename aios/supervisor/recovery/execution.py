from datetime import datetime, timezone


class RecoveryExecutionGate:


    def __init__(
        self,
        execution_queue=None,
    ):

        self.execution_queue = (
            execution_queue
        )



    def submit(
        self,
        review_result,
    ):

        if not review_result.get(
            "approved",
            False,
        ):

            return {
                "status":
                "rejected",

                "reason":
                "review_not_approved",
            }


        request = review_result.get(
            "request",
            {}
        )


        action = {
            "type":
            "recovery",

            "action":
            request.get(
                "action"
            ),

            "priority":
            request.get(
                "priority"
            ),

            "metadata":
            request.get(
                "metadata",
                {}
            ),

            "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
        }


        if self.execution_queue:

            self.execution_queue.enqueue(
                action
            )


        return {
            "status":
            "queued",

            "action":
            action,
        }
