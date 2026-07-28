from aios.core.factory import Factory

from .models import RecoveryProposal


class RecoveryPlanner:


    def create(
        self,
        health_decision,
    ):

        status = health_decision.get(
            "status",
            "unknown",
        )


        if status == "warning":

            return RecoveryProposal(
                action="inspect_runtime",
                reason="Runtime health warning detected",
                priority="medium",
                metadata=health_decision,
            )


        if status == "failed":

            return RecoveryProposal(
                action="prepare_recovery",
                reason="Runtime failure detected",
                priority="high",
                metadata=health_decision,
            )


        return RecoveryProposal(
            action="continue",
            reason="Runtime healthy",
            priority="low",
            metadata=health_decision,
        )
