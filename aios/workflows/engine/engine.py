from aios.execution.task_engine import TaskEngine, Task, TaskState

from .workflow import Workflow


class WorkflowEngine:

    def __init__(
        self,
        task_engine: TaskEngine | None = None,
        agent_context=None,
    ):
        self._task_engine = task_engine or TaskEngine()
        self.agent_context = agent_context

    @property
    def task_engine(self):
        return self._task_engine

    def submit(self, workflow: Workflow):
        for node in workflow.graph.topological_order():
            metadata = {}

            if self.agent_context:
                metadata = {
                    "agent_name": self.agent_context.agent_name,
                    "permission_level": (
                        self.agent_context.permissions.level.value
                    ),
                    "prompt_hash": (
                        self.agent_context.metadata.get(
                            "prompt_hash"
                        )
                    ),
                }

            task = Task(
                id=node.id,
                payload=node.payload,
                state=TaskState.READY,
                metadata=metadata,
            )
            self._task_engine.add(task)
        return workflow

    def ready(self):
        return self._task_engine.ready()
