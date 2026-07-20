from pathlib import Path
import json

from .models import MemoryEntry


class MemoryStore:

    def __init__(
        self,
        path=".aios/memory/store.json"
    ):
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.path.exists():
            self.path.write_text("[]")


    def save(
        self,
        entry: MemoryEntry
    ):

        data = self._load()

        data.append(
            entry.__dict__
        )

        self.path.write_text(
            json.dumps(
                data,
                indent=2
            )
        )

        return entry


    def all(self):

        return self._load()


    def find_category(
        self,
        category: str
    ):

        return [
            item
            for item in self._load()
            if item["category"] == category
        ]


    def _load(self):

        return json.loads(
            self.path.read_text()
        )
