from .base import IntegrityGuard


class CapabilityGuard(IntegrityGuard):


    name = "capability"



    def __init__(
        self,
        agent_manager=None,
    ):

        self.agent_manager = agent_manager



    def check(self):

        if not self.agent_manager:

            return {

                "guard":
                    self.name,

                "passed":
                    True,

                "reason":
                    "No agent manager attached",

            }


        registry = (
            self.agent_manager.registry
        )


        missing = []


        for agent in registry.agents.values():

            if not agent.capabilities:

                missing.append(
                    agent.name
                )


        return {

            "guard":
                self.name,

            "passed":
                len(missing) == 0,

            "missing":
                missing,

        }
