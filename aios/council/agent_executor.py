from aios.core.execution.runner import ExecutionRunner

from .agent_mapping import capabilities_for
from aios.agents.runtime.workspace import AgentWorkspace


class CouncilAgentExecutor(ExecutionRunner):


    def __init__(
        self,
        agent_manager,
    ):

        self.agent_manager = agent_manager

        self.workspace = AgentWorkspace()



    def ensure_agent(
        self,
        name,
    ):

        existing = (
            self.agent_manager.registry.get(
                name
            )
        )

        if existing:

            return existing


        return self.agent_manager.create_agent(
            name=name,
            role=f"{name} council agent",
            capabilities=capabilities_for(name),
        )



    async def review(
        self,
        agent_name,
        issue,
    ):

        agent = self.ensure_agent(
            agent_name
        )


        # Start runtime if needed

        if agent.state != "running":

            agent.start()


        analysis = (
            f"{agent_name} analyzed "
            f"{issue.title}\n\n"
            f"Capabilities:\n"
            f"{agent.capabilities}"
        )


        artifact = self.workspace.write(
            agent_name,
            "analysis.md",
            analysis,
        )


        return {

            "agent":
                agent_name,

            "capabilities":
                agent.capabilities,

            "analysis":
                analysis,

            "artifact":
                artifact,

        }
