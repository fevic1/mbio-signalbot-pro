from datetime import datetime, timezone


class RuntimeScheduler:

    def __init__(self):
        self._jobs = {}

    def register(self, name: str, job, interval=None):
        self._jobs[name] = {
            "job": job,
            "interval": interval,
            "last_run": None,
        }

        return self._jobs[name]

    def remove(self, name: str):
        return self._jobs.pop(name, None)

    def run(self, name: str):
        entry = self._jobs[name]

        result = entry["job"]()

        entry["last_run"] = datetime.now(
            timezone.utc
        ).isoformat()

        return result

    def run_all(self):
        results = {}

        for name in self._jobs:
            results[name] = self.run(name)

        return results

    def jobs(self):
        return tuple(sorted(self._jobs))

    def clear(self):
        self._jobs.clear()

    def __contains__(self, name):
        return name in self._jobs

    def __len__(self):
        return len(self._jobs)
