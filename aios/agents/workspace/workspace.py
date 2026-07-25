from pathlib import Path


class AgentWorkspace:


    def __init__(
        self,
        agent_name,
        root=".aios/workspaces",
    ):

        self.agent_name = agent_name

        self.path = (
            Path(root)
            /
            agent_name
        )


        self.path.mkdir(
            parents=True,
            exist_ok=True,
        )



    def write(
        self,
        filename,
        content,
    ):

        file = self.path / filename

        file.write_text(content)

        return file



    def describe(self):

        return {
            "agent": self.agent_name,
            "path": str(self.path),
        }
