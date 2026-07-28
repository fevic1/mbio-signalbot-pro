from aios.core.factory import Factory

from aios.learning.recommendation_model import (
    ImprovementProposal
)


class ImprovementReview:


    def __init__(
        self,
        council,
        consensus,
    ):

        self.council = council

        self.consensus = consensus



    def create(
        self,
        recommendation,
    ):

        return ImprovementProposal(
            recommendation
        )



    def submit(
        self,
        proposal,
    ):

        session = self.council.create_session(
            f"Should AIOS implement improvement: {proposal.recommendation}"
        )


        agents = [
            "architect",
            "risk",
            "skeptic",
            "verification",
        ]


        self.council.assign_agents(
            session,
            agents,
        )


        for agent in agents:

            self.council.add_response(
                session,
                agent,
                {
                    "analysis":
                        f"{agent} reviewed improvement proposal",
                    "artifact": {
                        "file":
                        f"{agent}_improvement_review.md"
                    }
                }
            )


        decision = self.council.finalize(
            session,
            self.consensus,
        )


        proposal.status = (
            "approved"
            if decision["approved"]
            else "rejected"
        )


        return {

            "proposal":
                proposal.describe(),

            "decision":
                decision,

        }
