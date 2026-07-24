from .models import OperationEvent


class ReleaseManager:


    def prepare(
        self,
        project,
    ):

        return OperationEvent(
            action="release.prepare",
            status="ready",
            details={
                "project": project.name,
                "message":
                    "Release preparation completed",
            },
        )


    def approve(
        self,
        release,
    ):

        release.status = "approved"

        return release
