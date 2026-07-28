from aios.core.registry import Registry


class AgentRegistry(Registry):

    def register(self, agent):
        return super().register(agent.name, agent)

    def list(self):
        return [
            agent.describe()
            for agent in self.all()
        ]
