from datetime import datetime, timezone


class RuntimeBootManager:

    def __init__(self, kernel):
        self._kernel = kernel
        self._booted = False
        self._steps = []

    def register(self, name: str, action):
        self._steps.append({
            "name": name,
            "action": action,
        })

    def boot(self):
        if self._booted:
            return False

        results = []

        for step in self._steps:
            result = step["action"]()

            results.append({
                "name": step["name"],
                "result": result,
            })

        self._booted = True

        return {
            "booted": True,
            "steps": results,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def status(self):
        return self._booted

    def steps(self):
        return tuple(
            step["name"]
            for step in self._steps
        )

    def reset(self):
        self._booted = False
