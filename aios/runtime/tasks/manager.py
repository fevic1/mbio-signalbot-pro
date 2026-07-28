from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True)
class RuntimeTask:
    id: str
    name: str
    state: str = "pending"
    payload: dict = field(default_factory=dict)
    created: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


class RuntimeTaskManager:

    def __init__(self):
        self._tasks = {}

    def create(self, name: str, payload=None):
        task = RuntimeTask(
            id=str(uuid.uuid4()),
            name=name,
            payload=payload or {},
        )

        self._tasks[task.id] = task
        return task

    def start(self, task_id: str):
        task = self._tasks[task_id]
        task.state = "running"
        return task

    def complete(self, task_id: str):
        task = self._tasks[task_id]
        task.state = "completed"
        return task

    def fail(self, task_id: str):
        task = self._tasks[task_id]
        task.state = "failed"
        return task

    def get(self, task_id: str):
        return self._tasks.get(task_id)

    def all(self):
        return tuple(self._tasks.values())

    def pending(self):
        return tuple(
            task
            for task in self._tasks.values()
            if task.state == "pending"
        )

    def clear(self):
        self._tasks.clear()

    def __len__(self):
        return len(self._tasks)
