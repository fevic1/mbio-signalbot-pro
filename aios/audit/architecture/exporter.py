import json
from pathlib import Path


class ArchitectureExporter:


    def __init__(
        self,
        output=".aios/audits/architecture/latest.json",
    ):
        self.output = Path(output)


    def export(self, items):

        self.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = [
            item.to_dict()
            for item in items
        ]

        self.output.write_text(
            json.dumps(
                data,
                indent=2,
            )
        )

        return self.output
