from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Skill:

    name: str

    domain: str

    description: str = ""

    capabilities: List[str] = field(
        default_factory=list
    )

    version: str = "1.0"

    status: str = "registered"

    metadata: Dict = field(
        default_factory=dict
    )


    def activate(self):

        self.status = "active"


    def deactivate(self):

        self.status = "inactive"


    def supports(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities


    def describe(self):

        return {
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
            "status": self.status,
        }
