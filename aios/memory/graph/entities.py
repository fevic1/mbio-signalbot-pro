from dataclasses import dataclass, field
from datetime import datetime, timezone

from aios.core.models import Node


@dataclass(slots=True)
class Entity(Node):
    entity_type: str = ""
    attributes: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
