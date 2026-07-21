from datetime import datetime
from .proposal import Proposal


class ProposalBuilder:

    def __init__(self):

        self.history = []


    def build(
        self,
        task,
        agent_results,
    ):

        proposal = Proposal(

            title=task["name"],

            description=self._description(
                agent_results
            ),

            category=task["category"],

            created_by="ProposalBuilder",
        )


        for agent_name, result in agent_results.items():

            confidence = self._confidence(
                result
            )

            proposal.add_opinion(

                agent=agent_name,

                opinion=result,

                confidence=confidence,
            )


        self.history.append(
            proposal
        )


        return proposal



    def _description(
        self,
        results,
    ):

        return (
            "Generated from multi-agent analysis: "
            +
            ", ".join(
                results.keys()
            )
        )



    def _confidence(
        self,
        result,
    ):

        if not result:

            return 0


        # Verification agents can override confidence later
        if isinstance(result, dict):

            if "verified" in result:

                return 1 if result["verified"] else 0.5


        return 0.75



    def history(self):

        return self.history
