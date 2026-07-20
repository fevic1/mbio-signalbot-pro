from pathlib import Path
import json

from .events import MemoryEvent


class EventStore:

    def __init__(
        self,
        path=".aios/memory/events.json"
    ):

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.path.exists():
            self.path.write_text("[]")


    def append(
        self,
        event: MemoryEvent
    ):

        events = self._load()

        events.append(
            event.to_dict()
        )

        self.path.write_text(
            json.dumps(
                events,
                indent=2
            )
        )

        return event


    def all(self):

        return self._load()


    def _load(self):

        return json.loads(
            self.path.read_text()
        )
