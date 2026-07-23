from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class Capability:

    name: str

    permission: str

    description: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    enabled: bool = True

    timeout: int = 60

    retry_limit: int = 2


    def validate(self):

        if not self.name:
            raise ValueError(
                "Capability name required"
            )

        if not self.permission:
            raise ValueError(
                "Capability permission required"
            )

        return True


    def snapshot(self):

        return {
            "name": self.name,
            "permission": self.permission,
            "description": self.description,
            "metadata": self.metadata,
            "enabled": self.enabled,
            "timeout": self.timeout,
            "retry_limit": self.retry_limit,
        }
