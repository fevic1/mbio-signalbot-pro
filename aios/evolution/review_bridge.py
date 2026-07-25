class EvolutionReviewBridge:


    def __init__(
        self,
        council,
        governance,
    ):

        self.council = council

        self.governance = governance



    def review(
        self,
        proposal,
    ):

        council_result = self.council.evaluate(
            proposal
        )


        governance_result = self.governance.validate(
            council_result
        )


        return {

            "proposal":
                proposal,

            "council":
                council_result,

            "governance":
                governance_result,

            "approved":
                governance_result.get(
                    "passed",
                    False,
                ),

        }
