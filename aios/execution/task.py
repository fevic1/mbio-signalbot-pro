from dataclasses import dataclass
from uuid import uuid4


@dataclass
class CapabilityTask:

    worker: object
    id: str = None
    result: object = None
    status: str = "pending"
    error: str = None

    def __post_init__(self):

        if self.id is None:
            self.id = str(uuid4())
