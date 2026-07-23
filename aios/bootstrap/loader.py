class AgentBootstrap:


    def __init__(
        self,
        registry,
        memory=None
    ):

        self.registry = registry
        self.memory = memory


    def load_capabilities(self):

        capabilities = [

            {
                "name": "can_search",
                "permission": "research",
            },

            {
                "name": "can_reason",
                "permission": "research",
            },

            {
                "name": "can_plan",
                "permission": "planning",
            },

            {
                "name": "can_review",
                "permission": "review",
            },

            {
                "name": "can_verify",
                "permission": "verification",
            },

            {
                "name": "can_execute",
                "permission": "execution",
            },

        ]


        for item in capabilities:

            self.registry.register(
                item["name"],
                item["permission"],
            )


        return self.registry.list_capabilities()
