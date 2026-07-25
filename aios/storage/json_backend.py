import json
from pathlib import Path

from .backend import StorageBackend
from .migrations import MigrationManager
from .atomic import AtomicWriter


class JSONBackend(StorageBackend):


    def __init__(
        self,
        root=".aios/audit",
    ):

        self.root = Path(root)

        self.migrations = MigrationManager()

        self.atomic = AtomicWriter()

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )


        self.files = {

            "decisions":
                self.root / "decisions.json",

            "sessions":
                self.root / "sessions.json",

            "governance":
                self.root / "governance.json",

            "decision_records":
                self.root / "decision_records.json",

            "changes":
                self.root / "changes.json",

        }


        for path in self.files.values():

            if not path.exists():

                path.write_text(
                    '{"schema_version": 1, "records": []}'
                )



    def append(
        self,
        category,
        data,
    ):

        path = self.files[category]


        payload = self.migrations.migrate(
            json.loads(
                path.read_text()
            )
        )


        payload["records"].append(
            data
        )


        self.atomic.write(
            path,
            payload,
        )



    def read(
        self,
        category,
    ):

        payload = self.migrations.migrate(
            json.loads(
                self.files[category].read_text()
            )
        )


        return payload.get(
            "records",
            []
        )
