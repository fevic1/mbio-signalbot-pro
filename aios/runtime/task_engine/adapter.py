from datetime import datetime, timezone
import uuid

from aios.execution.task_engine import (
    TaskEngine as CanonicalTaskEngine,
)

from aios.execution.task_engine.task import (
    Task,
    TaskState,
)


class TaskEngineAdapter:

    def __init__(self):
        self.engine = CanonicalTaskEngine()

    def create(
        self,
        name,
        payload=None,
        priority=0,
    ):

        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            payload=payload or {},
            priority=priority,
            created=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        self.engine.add(task)

        return self._serialize(task)


    def start(self, task_id):

        self.engine.set_state(
            task_id,
            TaskState.RUNNING,
        )

        return self.get(task_id)


    def complete(
        self,
        task_id,
        result=None,
    ):

        self.engine.complete(task_id)

        task = self.engine.get(task_id)

        if result is not None:
            task.result = result

        return self._serialize(task)


    def fail(
        self,
        task_id,
        error,
    ):

        self.engine.fail(task_id)

        task = self.engine.get(task_id)
        task.error = str(error)

        return self._serialize(task)


    def get(self, task_id):

        return self._serialize(
            self.engine.get(task_id)
        )


    def list(self):

        return tuple(
            self._serialize(task)
            for task in self.engine._tasks.values()
        )


    def _serialize(self, task):

        return {
            "id": task.id,
            "name": task.name,
            "payload": getattr(
                task,
                "payload",
                {},
            ),
            "priority": getattr(
                task,
                "priority",
                0,
            ),
            "status": task.state.value,
        }
