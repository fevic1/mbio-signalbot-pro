from .agent import Agent, AgentState


class AgentRuntime:

    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent):
        self._agents[agent.id] = agent
        return agent

    def unregister(self, agent_id: str):
        return self._agents.pop(agent_id, None)

    def get(self, agent_id: str):
        return self._agents[agent_id]

    def start(self, agent_id: str):
        self._agents[agent_id].state = AgentState.RUNNING

    def stop(self, agent_id: str):
        self._agents[agent_id].state = AgentState.STOPPED

    def fail(self, agent_id: str):
        self._agents[agent_id].state = AgentState.FAILED

    def ready(self, agent_id: str):
        self._agents[agent_id].state = AgentState.READY

    def running(self):
        return [
            agent
            for agent in self._agents.values()
            if agent.state is AgentState.RUNNING
        ]

    def __contains__(self, agent_id):
        return agent_id in self._agents

    def __len__(self):
        return len(self._agents)
