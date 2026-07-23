from .models import TaskGraph, TaskNode


class TaskGraphManager:


    def create(
        self,
        project_id,
        tasks,
    ):

        graph = TaskGraph(
            project_id
        )


        for task in tasks:

            graph.add(
                TaskNode(
                    name=task["name"],
                    capability=task["capability"],
                    depends_on=task.get(
                        "depends_on",
                        []
                    ),
                )
            )


        return graph
