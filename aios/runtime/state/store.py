import json
from pathlib import Path


class RuntimeStateStore:


    def __init__(
        self,
        path=None,
    ):

        self.path = Path(
            path
            or ".aios/runtime_state.json"
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


    def save(
        self,
        state,
    ):

        self.path.write_text(
            json.dumps(
                state.describe(),
                indent=2,
            )
        )

        return state


    def load(
        self,
    ):

        if not self.path.exists():

            return None


        return json.loads(
            self.path.read_text()
        )


    def clear(
        self,
    ):

        if self.path.exists():

            self.path.unlink()
