from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class MemoryEntry:

    category: str
    key: str
    value: str

    source: str = "aios"

    timestamp: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    importance: str = "normal"

    links: List[str] = field(
        default_factory=list
    )
