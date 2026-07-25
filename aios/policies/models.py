from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class PolicyVersion:

    name: str

    content: str

    version: int = 1

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

            "id":
                self.id,

            "name":
                self.name,

            "version":
                self.version,

            "content":
                self.content,

            "created_at":
                self.created_at,

        }
