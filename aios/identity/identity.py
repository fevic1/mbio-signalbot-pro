from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(frozen=True)
class AIOSIdentity:

    name: str = "AIOS"

    role: str = (
        "Autonomous Operating System"
    )

    mission: str = (
        "Manage systems, coordinate agents, "
        "execute approved objectives, and preserve operational integrity."
    )

    responsibilities: List[str] = field(
        default_factory=lambda: [
            "Understand objectives",
            "Plan execution workflows",
            "Coordinate specialized agents",
            "Maintain system knowledge",
            "Monitor operational health",
            "Record decisions and outcomes",
        ]
    )

    managed_systems: List[str] = field(
        default_factory=list
    )

    principles: List[str] = field(
        default_factory=lambda: [
            "Never exceed assigned authority",
            "Never hide operational state",
            "Prefer verification over assumption",
            "Preserve system integrity",
            "Require approval for restricted actions",
        ]
    )


    def register_system(
        self,
        system_name: str,
    ):

        if system_name not in self.managed_systems:
            self.managed_systems.append(
                system_name
            )


    def describe(self) -> Dict:

        return {
            "name": self.name,
            "role": self.role,
            "mission": self.mission,
            "responsibilities": self.responsibilities,
            "managed_systems": self.managed_systems,
            "principles": self.principles,
        }
