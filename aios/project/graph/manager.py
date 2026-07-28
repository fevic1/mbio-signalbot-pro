from aios.core.service import Service

from aios.planning.task_graph import TaskGraphFactory


class TaskGraphManager:
    create = staticmethod(TaskGraphFactory.from_tasks)
