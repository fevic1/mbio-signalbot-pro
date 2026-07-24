from .models import OperationEvent


class DeploymentManager:


    def deploy(
        self,
        release,
    ):

        if release.status != "approved":

            raise ValueError(
                "Release not approved"
            )


        return OperationEvent(
            action="deployment.execute",
            status="completed",
            details={
                "release_id": release.id,
            },
        )
