
from datetime import datetime, timezone
import uuid


class TaskEngine:

    def __init__(self):
        self.tasks = {}

    def create(self, name, payload=None, priority=0):
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "name": name,
            "payload": payload or {},
            "priority": priority,
            "status": "pending",
            "created": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.tasks[task_id] = task
        return task

    def start(self, task_id):
        self.tasks[task_id]["status"] = "running"
        return self.tasks[task_id]

    def complete(self, task_id, result=None):
        task = self.tasks[task_id]
        task["status"] = "completed"
        task["result"] = result
        return task

    def fail(self, task_id, error):
        task = self.tasks[task_id]
        task["status"] = "failed"
        task["error"] = str(error)
        return task

    def get(self, task_id):
        return self.tasks.get(task_id)

    def list(self):
        return tuple(self.tasks.values())
