from datetime import datetime, timezone
import json


class RuntimeCheckpoint:

    def __init__(self, kernel):
        self._kernel = kernel
        self._checkpoints = []

    def create(self, name="checkpoint"):
        checkpoint = {
            "name": name,
            "created": datetime.now(
                timezone.utc
            ).isoformat(),
            "state": self._kernel.state.value,
            "version": self._kernel.version.string,
            "services": list(
                self._kernel.services()
            ),
            "context": dict(
                self._kernel.context.items()
            ),
            "config": self._kernel.config.export(),
        }

        self._checkpoints.append(checkpoint)
        return checkpoint

    def latest(self):
        return (
            self._checkpoints[-1]
            if self._checkpoints
            else None
        )

    def all(self):
        return tuple(self._checkpoints)

    def restore(self, checkpoint):
        self._kernel.context.update(
            checkpoint.get("context", {})
        )
        self._kernel.config.update(
            checkpoint.get("config", {})
        )

        return True

    def export(self):
        return json.loads(
            json.dumps(self._checkpoints)
        )

    def clear(self):
        self._checkpoints.clear()

    def __len__(self):
        return len(self._checkpoints)
