class PolicyRuntime:


    def __init__(
        self,
        policy_context,
    ):

        self.policy_context = policy_context



    def attach(
        self,
        gate,
        result,
    ):

        policy = self.policy_context.get(
            gate
        )

        result["policy"] = policy

        return result
