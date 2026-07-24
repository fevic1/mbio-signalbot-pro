from dataclasses import dataclass, field
import uuid
from datetime import datetime, timezone


@dataclass
class Entity:

    name: str

    entity_type: str

    attributes: dict = field(
        default_factory=dict
    )

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(self):

        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "attributes": self.attributes,
            "created_at": self.created_at,
        }
