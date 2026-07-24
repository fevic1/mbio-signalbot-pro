from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SpecialistAgent:

    name: str

    role: str

    domain: str

    capabilities: List[str] = field(
        default_factory=list
    )

    description: str = ""

    status: str = "available"

    metadata: Dict = field(
        default_factory=dict
    )


    def can_handle(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities


    def assign(self):

        self.status = "assigned"


    def release(self):

        self.status = "available"


    def describe(self):

        return {
            "name": self.name,
            "role": self.role,
            "domain": self.domain,
            "capabilities": self.capabilities,
            "status": self.status,
        }
