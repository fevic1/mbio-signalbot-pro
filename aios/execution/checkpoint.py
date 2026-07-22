import json
from pathlib import Path


class CheckpointManager:

    def __init__(self, directory="runtime/checkpoints"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, context):
        path = self.directory / f"{context.id}.json"

        with open(path, "w") as f:
            json.dump(
                context.snapshot(),
                f,
                indent=2,
            )

        return str(path)

    def load(self, context_id):
        path = self.directory / f"{context_id}.json"

        if not path.exists():
            return None

        with open(path) as f:
            return json.load(f)

    def delete(self, context_id):
        path = self.directory / f"{context_id}.json"

        if path.exists():
            path.unlink()
