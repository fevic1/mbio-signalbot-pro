class PolicyProposal:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def apply(
        self,
        proposal,
    ):

        recommendation = (
            proposal["recommendation"]
        )


        return self.registry.update(
            recommendation["area"],
            recommendation["recommendation"],
        )
