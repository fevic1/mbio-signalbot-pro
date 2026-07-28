from datetime import datetime, timezone


class RuntimeOrchestrator:

    def __init__(self, kernel):
        self._kernel = kernel
        self._flows = {}

    def register(self, name: str, workflow):
        self._flows[name] = workflow
        return workflow

    def remove(self, name: str):
        return self._flows.pop(name, None)

    def execute(self, name: str, *args, **kwargs):
        workflow = self._flows[name]

        started = datetime.now(timezone.utc)

        result = workflow(*args, **kwargs)

        return {
            "workflow": name,
            "result": result,
            "started": started.isoformat(),
            "finished": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def list(self):
        return tuple(sorted(self._flows))

    def clear(self):
        self._flows.clear()

    def __contains__(self, name):
        return name in self._flows

    def __len__(self):
        return len(self._flows)
