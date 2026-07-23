from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CapabilityRequest:

    capability: str

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    permission: str = ""

    retry_limit: int = 2
