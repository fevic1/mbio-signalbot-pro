import json
import uuid
from pathlib import Path
from datetime import datetime, timezone


class PolicyRegistry:


    def __init__(
        self,
        root=".aios/policies",
    ):

        self.root = Path(root)

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )


        self.file = (
            self.root /
            "policies.json"
        )


        if not self.file.exists():

            self.file.write_text(
                "[]"
            )



    def register(
        self,
        policy,
    ):

        policies = json.loads(
            self.file.read_text()
        )


        entry = {

            "id":
                str(uuid.uuid4()),

            "version":
                len(policies) + 1,

            "policy":
                policy,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        policies.append(
            entry
        )


        self.file.write_text(
            json.dumps(
                policies,
                indent=2
            )
        )


        return entry



    def history(self):

        return json.loads(
            self.file.read_text()
        )
