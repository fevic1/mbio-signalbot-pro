from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ManagedSystem:

    name: str

    system_type: str

    domain: str

    description: str = ""

    capabilities: List[str] = field(
        default_factory=list
    )

    status: str = "unknown"

    metadata: Dict = field(
        default_factory=dict
    )


    def activate(self):

        self.status = "online"


    def deactivate(self):

        self.status = "offline"


    def has_capability(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities


    def describe(self):

        return {
            "name": self.name,
            "type": self.system_type,
            "domain": self.domain,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
        }
