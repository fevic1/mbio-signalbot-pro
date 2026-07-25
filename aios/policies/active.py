from .binding import PolicyBinding


class ActivePolicyManager:


    def __init__(self):

        self.bindings = []



    def activate(
        self,
        policy,
        decision,
        session,
    ):

        binding = PolicyBinding(

            policy_name=
                policy["name"],

            policy_version=
                policy["version"],

            decision_id=
                decision.get(
                    "id"
                ),

            session_id=
                session.get(
                    "id"
                ),

            evidence=
                decision.get(
                    "governance",
                    {}
                ).get(
                    "results",
                    []
                ),

            governance=
                decision.get(
                    "governance",
                    {}
                ),

        )


        self.bindings.append(
            binding
        )


        return binding.describe()



    def history(self):

        return [

            item.describe()

            for item in self.bindings

        ]
