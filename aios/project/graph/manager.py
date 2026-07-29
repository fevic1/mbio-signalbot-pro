from aios.core.service import Service


class TaskGraphManager:

    @staticmethod
    def create(*args, **kwargs):
        from aios.planning.task_graph import TaskGraphFactory

        return TaskGraphFactory.from_tasks(
            *args,
            **kwargs,
        )
