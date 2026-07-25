class PolicyEvaluator:


    def __init__(
        self,
        loader,
    ):

        self.loader = loader



    def evaluate(
        self,
        change,
    ):

        policies = self.loader.load()


        matches = []


        for policy in policies:

            stored = policy.get(
                "policy",
                {}
            )


            proposal = stored.get(
                "proposal",
                {}
            )


            if (
                proposal.get("area")
                ==
                change.get("area")
            ):

                matches.append(
                    policy
                )


        return {

            "allowed":
                True,

            "matched_policies":
                matches,

            "count":
                len(matches),

        }
