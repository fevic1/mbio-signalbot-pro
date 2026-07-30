from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass(slots=True)
class AuditEvent:
    event_type: str
    timestamp: str
    agent: str = ""
    task_id: str = ""
    prompt_hash: str = ""
    decision: str = ""
    metadata: Dict[str, Any] | None = None

    def serialize(self):
        return asdict(self)
