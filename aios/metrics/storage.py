import json
import os
from datetime import datetime, timezone


METRICS_PATH = "data/aios_metrics.json"


class MetricsStore:

    def __init__(
        self,
        path=METRICS_PATH,
    ):

        self.path = path

        self._ensure_dir()


    def _ensure_dir(self):

        directory = os.path.dirname(
            self.path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True,
            )


    def save(
        self,
        snapshot: dict,
    ):

        history = self.load()

        entry = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "snapshot": snapshot,
        }

        history.append(
            entry
        )

        with open(
            self.path,
            "w",
        ) as f:

            json.dump(
                history,
                f,
                indent=2,
            )

        return entry


    def load(self):

        if not os.path.exists(
            self.path
        ):
            return []


        try:

            with open(
                self.path,
                "r",
            ) as f:

                return json.load(
                    f
                )

        except (
            json.JSONDecodeError,
            IOError,
        ):

            return []


    def latest(self):

        history = self.load()

        if not history:
            return None

        return history[-1]
