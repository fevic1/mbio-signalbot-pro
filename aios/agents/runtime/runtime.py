from .agent import Agent, AgentState
from aios.runtime.prompt_loader import PromptLoader, AgentExecutionContext


from aios.runtime.prompt_loader import PromptLoader


class AgentRuntime:

    def __init__(self, root_dir=None):
        self._agents: dict[str, Agent] = {}

        self.prompt_loader = PromptLoader(
            root_dir=root_dir
        )

        self.active_contexts: dict[str, AgentExecutionContext] = {}
        self._prompt_loader = PromptLoader()
        self._contexts = {}

    def register(self, agent: Agent):
        self._agents[agent.id] = agent
        return agent

    def prepare_agent(self, agent_name: str):
        context = self.prompt_loader.assemble_context(
            agent_name
        )

        self.active_contexts[agent_name] = context

        return context

    def context(self, agent_name: str):
        return self.active_contexts.get(agent_name)

    def load_context(self, agent_name: str):
        context = self._prompt_loader.assemble_context(
            agent_name
        )

        self._contexts[agent_name] = context

        return context

    def context(self, agent_name: str):
        return self._contexts.get(agent_name)

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
