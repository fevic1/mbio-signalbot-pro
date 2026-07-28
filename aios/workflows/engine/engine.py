from aios.execution.task_engine import TaskEngine, Task, TaskState

from .workflow import Workflow


class WorkflowEngine:

    def __init__(self, task_engine: TaskEngine | None = None):
        self._task_engine = task_engine or TaskEngine()

    @property
    def task_engine(self):
        return self._task_engine

    def submit(self, workflow: Workflow):
        for node in workflow.graph.topological_order():
            task = Task(
                id=node.id,
                payload=node.payload,
                state=TaskState.READY,
            )
            self._task_engine.add(task)
        return workflow

    def ready(self):
        return self._task_engine.ready()
