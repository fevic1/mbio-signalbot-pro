from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True)
class RuntimeWorker:
    id: str
    name: str
    state: str = "idle"
    metadata: dict = field(default_factory=dict)
    created: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


class RuntimeWorkerManager:

    def __init__(self):
        self._workers = {}

    def register(
        self,
        name: str,
        metadata=None,
    ):
        worker = RuntimeWorker(
            id=str(uuid.uuid4()),
            name=name,
            metadata=metadata or {},
        )

        self._workers[worker.id] = worker
        return worker

    def start(self, worker_id: str):
        worker = self._workers[worker_id]
        worker.state = "running"
        return worker

    def stop(self, worker_id: str):
        worker = self._workers[worker_id]
        worker.state = "stopped"
        return worker

    def get(self, worker_id: str):
        return self._workers.get(worker_id)

    def active(self):
        return tuple(
            worker
            for worker in self._workers.values()
            if worker.state == "running"
        )

    def all(self):
        return tuple(self._workers.values())

    def clear(self):
        self._workers.clear()

    def __len__(self):
        return len(self._workers)
