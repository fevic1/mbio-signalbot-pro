from .task import Task, TaskState


class TaskEngine:

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task):
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str):
        return self._tasks[task_id]

    def ready(self):
        return [
            t
            for t in self._tasks.values()
            if t.state is TaskState.READY
        ]

    def set_state(self, task_id: str, state: TaskState):
        self._tasks[task_id].state = state

    def cancel(self, task_id: str):
        self.set_state(task_id, TaskState.CANCELLED)

    def complete(self, task_id: str):
        self.set_state(task_id, TaskState.COMPLETED)

    def fail(self, task_id: str):
        self.set_state(task_id, TaskState.FAILED)

    def __len__(self):
        return len(self._tasks)
