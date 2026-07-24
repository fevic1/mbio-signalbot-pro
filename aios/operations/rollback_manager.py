from .models import OperationEvent


class RollbackManager:


    def rollback(
        self,
        deployment,
    ):

        return OperationEvent(
            action="deployment.rollback",
            status="completed",
            details={
                "deployment": deployment.id,
            },
        )
