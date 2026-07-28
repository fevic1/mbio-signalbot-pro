from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True)
class RuntimeIntent:
    id: str
    name: str
    goal: str
    metadata: dict = field(default_factory=dict)
    created: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


class RuntimeIntentManager:

    def __init__(self):
        self._intents = {}

    def create(
        self,
        name: str,
        goal: str,
        metadata=None,
    ):
        intent = RuntimeIntent(
            id=str(uuid.uuid4()),
            name=name,
            goal=goal,
            metadata=metadata or {},
        )

        self._intents[intent.id] = intent
        return intent

    def get(self, intent_id: str):
        return self._intents.get(intent_id)

    def remove(self, intent_id: str):
        return self._intents.pop(intent_id, None)

    def all(self):
        return tuple(self._intents.values())

    def clear(self):
        self._intents.clear()

    def __len__(self):
        return len(self._intents)
