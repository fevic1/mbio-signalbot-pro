from .registry import PolicyRegistry
from .change_log import PolicyChangeLog


class PolicyEvolution:


    def __init__(self):

        self.registry = PolicyRegistry()

        self.log = PolicyChangeLog()



    def apply(
        self,
        proposal,
        decision,
    ):

        if not decision.get(
            "approved",
            False
        ):

            raise ValueError(
                "Cannot apply rejected policy"
            )


        policy = {

            "proposal":
                proposal,

            "decision":
                decision,

        }


        registered = (
            self.registry.register(
                policy
            )
        )


        self.log.record(
            registered
        )


        return registered
