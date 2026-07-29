from aios.core.service import Service


class TaskGraphBuilder:

    @staticmethod
    def build(*args, **kwargs):
        from aios.planning.task_graph import TaskGraphFactory

        return TaskGraphFactory.from_project(
            *args,
            **kwargs,
        )
