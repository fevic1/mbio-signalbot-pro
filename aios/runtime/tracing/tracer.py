from datetime import datetime, timezone
import uuid


class RuntimeTracer:

    def __init__(self):
        self._spans = {}

    def start(self, name: str, metadata=None):
        trace_id = str(uuid.uuid4())

        self._spans[trace_id] = {
            "id": trace_id,
            "name": name,
            "metadata": metadata or {},
            "state": "running",
            "started": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        return trace_id

    def finish(self, trace_id: str, result=None):
        span = self._spans[trace_id]

        span["state"] = "completed"
        span["result"] = result
        span["finished"] = datetime.now(
            timezone.utc
        ).isoformat()

        return span

    def fail(self, trace_id: str, error):
        span = self._spans[trace_id]

        span["state"] = "failed"
        span["error"] = str(error)
        span["finished"] = datetime.now(
            timezone.utc
        ).isoformat()

        return span

    def get(self, trace_id: str):
        return self._spans.get(trace_id)

    def all(self):
        return tuple(self._spans.values())

    def clear(self):
        self._spans.clear()

    def __len__(self):
        return len(self._spans)
