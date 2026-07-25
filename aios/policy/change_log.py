import json
from pathlib import Path


class PolicyChangeLog:


    def __init__(
        self,
        root=".aios/policies",
    ):

        self.file = (
            Path(root) /
            "changes.json"
        )

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        if not self.file.exists():

            self.file.write_text(
                "[]"
            )



    def record(
        self,
        change,
    ):

        items = json.loads(
            self.file.read_text()
        )


        items.append(
            change
        )


        self.file.write_text(
            json.dumps(
                items,
                indent=2
            )
        )


        return change
