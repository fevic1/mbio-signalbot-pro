class PolicyContext:


    def __init__(
        self,
        resolver,
    ):

        self.resolver = resolver



    def get(
        self,
        policy_name,
    ):

        return self.resolver.resolve(
            policy_name
        )
