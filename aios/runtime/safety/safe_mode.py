from datetime import datetime, timezone
from pathlib import Path
import json


class SafeMode:

    def __init__(self, root_dir="."):
        self.path = (
            Path(root_dir)
            / ".aios"
            / "memory"
            / "crash_dumps"
        )

        self.path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.active = False


    def activate(
        self,
        reason,
        state=None,
    ):

        self.active = True

        dump = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "reason": str(reason),
            "state": state or {},
        }

        file = (
            self.path
            / "safe_mode_dump.json"
        )

        file.write_text(
            json.dumps(
                dump,
                indent=2,
                default=str,
            )
        )

        return dump


    def is_active(self):
        return self.active
