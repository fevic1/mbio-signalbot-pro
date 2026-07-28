from aios.core.identifiable import Identifiable

from pathlib import Path
from datetime import datetime, timezone


class AgentWorkspace(Identifiable):


    def __init__(
        self,
        root=".aios/workspaces",
    ):

        self.root = Path(root)

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )



    def write(
        self,
        agent,
        filename,
        content,
    ):

        directory = (
            self.root /
            agent
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


        path = directory / filename

        path.write_text(
            content
        )

        return {
            "agent": agent,
            "file": str(path),
            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }
