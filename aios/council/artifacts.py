from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CouncilArtifact:

    name: str

    content: str

    creator: str

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


    def describe(
        self,
    ):

        return {
            "id": self.id,
            "name": self.name,
            "creator": self.creator,
            "content": self.content,
            "created_at": self.created_at,
        }



class ArtifactStore:


    def __init__(self):

        self.artifacts = []



    def add(
        self,
        artifact,
    ):

        self.artifacts.append(
            artifact
        )

        return artifact



    def list(
        self,
    ):

        return [
            item.describe()
            for item
            in self.artifacts
        ]
