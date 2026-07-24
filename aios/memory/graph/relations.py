from dataclasses import dataclass
import uuid


@dataclass
class Relation:

    source: str

    relation: str

    target: str

    id: str = None


    def __post_init__(self):

        if self.id is None:

            self.id = str(
                uuid.uuid4()
            )


    def describe(self):

        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
        }
