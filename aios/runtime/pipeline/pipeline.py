from datetime import datetime, timezone


class RuntimePipeline:

    def __init__(self):
        self._stages = []

    def add(self, name: str, handler):
        self._stages.append({
            "name": name,
            "handler": handler,
        })

        return handler

    def execute(self, payload=None):
        result = payload

        started = datetime.now(timezone.utc)

        for stage in self._stages:
            result = stage["handler"](result)

        return {
            "result": result,
            "stages": [
                stage["name"]
                for stage in self._stages
            ],
            "started": started.isoformat(),
            "finished": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def stages(self):
        return tuple(
            stage["name"]
            for stage in self._stages
        )

    def clear(self):
        self._stages.clear()

    def __len__(self):
        return len(self._stages)
