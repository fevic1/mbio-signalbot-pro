from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, timezone
import uuid


@dataclass
class MissionTeam:

    project_id: str

    objective: str

    agents: List[Dict] = field(
        default_factory=list
    )

    status: str = "created"

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def add_agent(
        self,
        agent,
    ):

        self.agents.append(
            agent.describe()
            if hasattr(agent, "describe")
            else agent
        )


    def activate(self):

        self.status = "active"


    def describe(self):

        return {
            "id": self.id,
            "project_id": self.project_id,
            "objective": self.objective,
            "agents": self.agents,
            "status": self.status,
            "created_at": self.created_at,
        }



class MissionBuilder:


    def __init__(
        self,
        workforce_manager,
    ):

        self.workforce_manager = (
            workforce_manager
        )


    def assemble(
        self,
        project,
        capabilities,
    ):

        team = MissionTeam(
            project_id=project.id,
            objective=(
                project.description
                or project.name
            ),
        )


        agents = (
            self.workforce_manager
            .assemble_team(
                capabilities
            )
        )


        for agent in agents:

            team.add_agent(
                agent
            )


        team.activate()


        return team
