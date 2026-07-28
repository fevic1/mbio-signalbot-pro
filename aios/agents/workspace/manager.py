from aios.core.identifiable import Identifiable

from aios.core.factory import Factory

from .workspace import AgentWorkspace
from .context import AgentContext


class WorkspaceManager(Identifiable):


    def __init__(self):

        self.workspaces = {}



    def create(
        self,
        agent,
    ):

        workspace = AgentWorkspace(
            agent.name
        )


        context = AgentContext(
            agent_id=agent.id,
            memory_id=f"agent:{agent.name}",
        )


        self.workspaces[
            agent.name
        ] = {
            "workspace": workspace,
            "context": context,
        }


        agent.memory_id = (
            context.memory_id
        )


        return context



    def get(
        self,
        agent_name,
    ):

        return self.workspaces.get(
            agent_name
        )



    def describe(self):

        return {
            name:
            item["context"].describe()

            for name, item
            in self.workspaces.items()
        }
