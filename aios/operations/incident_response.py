from aios.core.factory import Factory

from .models import OperationEvent


class IncidentResponse:


    def create(
        self,
        issue,
    ):

        return OperationEvent(
            action="incident.created",
            status="open",
            details={
                "issue": issue,
            },
        )


    def resolve(
        self,
        incident,
    ):

        incident.status = "resolved"

        return incident
