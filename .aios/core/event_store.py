#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


class EventStore:

    def __init__(self):
        self.path = Path(".aios/memory/events.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text("[]")

    def _load(self):
        with self.path.open() as f:
            return json.load(f)

    def _save(self, events):
        with self.path.open("w") as f:
            json.dump(events, f, indent=2)

    def append(self, event, payload=None):

        events = self._load()

        events.append({
            "id": len(events) + 1,
            "time": datetime.utcnow().isoformat(timespec="seconds"),
            "event": event,
            "payload": payload or {}
        })

        self._save(events)

    def all(self):
        return self._load()

    def last(self, n=10):
        return self._load()[-n:]

    def count(self):
        return len(self._load())


event_store = EventStore()


if __name__ == "__main__":

    event_store.append(
        "kernel.started",
        {"version": "1.0.0"}
    )

    event_store.append(
        "plugin.loaded",
        {"plugin": "superpowers"}
    )

    print(event_store.count())
    print(event_store.last())
