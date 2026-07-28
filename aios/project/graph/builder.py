from aios.core.service import Service

from aios.planning.task_graph import TaskGraphFactory


class TaskGraphBuilder:
    build = staticmethod(TaskGraphFactory.from_project)
