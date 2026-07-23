from dataclasses import dataclass
from uuid import uuid4


@dataclass
class CapabilityTask:

    capability: str
    id: str = None
    result: object = None
    status: str = "pending"

    def __post_init__(self):

        if self.id is None:
            self.id = str(uuid4())
