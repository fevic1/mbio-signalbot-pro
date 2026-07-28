from dataclasses import dataclass, field
from ..ids import new_id


@dataclass(slots=True)
class Relationship:
    source: str
    target: str
    kind: str
    id: str = field(default_factory=new_id)
    metadata: dict = field(default_factory=dict)
