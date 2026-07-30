class AgentRouter:

    def __init__(self):

        self.routes = {}


    def register(
        self,
        name,
        agent,
    ):

        self.routes[name] = agent


    def resolve(
        self,
        name,
    ):

        return self.routes.get(
            name
        )
