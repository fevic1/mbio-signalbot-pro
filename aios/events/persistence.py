import json
from pathlib import Path


class EventPersistence:

    def __init__(
        self,
        path=".aios/memory/events.json",
    ):

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


    def append(
        self,
        event,
    ):

        events = self.load()

        record = event.to_dict()

        event_id = (
            record.get("timestamp")
            or str(record)
        )

        existing = [
            e.get("timestamp")
            for e in events
        ]

        if event_id in existing:
            return False


        events.append(
            record
        )

        self.path.write_text(
            json.dumps(
                events,
                indent=2,
            )
        )

        return True


    def load(
        self,
    ):

        if not self.path.exists():
            return []


        try:

            return json.loads(
                self.path.read_text()
            )

        except json.JSONDecodeError:

            return []
