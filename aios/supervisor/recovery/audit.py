from datetime import datetime, timezone


class RecoveryAuditWriter:


    def __init__(
        self,
        memory_router=None,
    ):

        self.memory_router = (
            memory_router
        )



    def record(
        self,
        execution_result,
    ):

        record = {
            "type":
            "operational",

            "event":
            "recovery_execution",

            "result":
            execution_result,

            "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),
        }


        if self.memory_router:

            self.memory_router.store(
                record
            )


        return record
