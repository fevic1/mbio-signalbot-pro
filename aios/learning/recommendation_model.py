from dataclasses import dataclass
import uuid


@dataclass
class ImprovementProposal:

    recommendation: dict

    id: str = None

    status: str = "proposed"


    def __post_init__(self):

        if self.id is None:

            self.id = str(
                uuid.uuid4()
            )


    def describe(self):

        return {

            "id":
                self.id,

            "recommendation":
                self.recommendation,

            "status":
                self.status,

        }
