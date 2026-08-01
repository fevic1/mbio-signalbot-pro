import json
from pathlib import Path


class EventPersistence:

    def __init__(
        self,
        path=".aios/memory/events.json",
        max_records=5000,
    ):
        self.path = Path(path)
        self.max_records = max_records

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def append(self, event):
        events = self.load()

        if hasattr(event, "describe"):
            record = event.describe()
        elif hasattr(event, "to_dict"):
            record = event.to_dict()
        else:
            return False

        event_id = record.get("id")

        if event_id and any(
            item.get("id") == event_id
            for item in events
        ):
            return False

        events.append(record)
        events = events[-self.max_records:]

        temporary = self.path.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                events,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )

        temporary.replace(self.path)
        return True

    def load(self):
        if not self.path.exists():
            return []

        try:
            data = json.loads(
                self.path.read_text()
            )
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
