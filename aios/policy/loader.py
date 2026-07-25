import json
from pathlib import Path


class PolicyLoader:


    def __init__(
        self,
        root=".aios/policies",
    ):

        self.file = (
            Path(root) /
            "policies.json"
        )



    def load(
        self,
    ):

        if not self.file.exists():

            return []


        return json.loads(
            self.file.read_text()
        )
