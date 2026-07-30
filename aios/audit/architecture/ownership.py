from pathlib import Path
import json


class OwnershipRegistry:

    def __init__(
        self,
        path=".aios/governance/component_ownership.json",
    ):
        self.path = Path(path)
        self.data = {}

        if self.path.exists():
            self.data = json.loads(
                self.path.read_text()
            )


    def get(self, component):
        return self.data.get(
            component,
            {}
        )


    def owner(self, component):
        return self.get(component).get(
            "canonical"
        )


    def status(self, component):
        return self.get(component).get(
            "status",
            "untracked"
        )


    def save(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                self.data,
                indent=2,
            )
        )
