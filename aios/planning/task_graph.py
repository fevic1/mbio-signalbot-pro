from aios.project.graph.models import TaskGraph, TaskNode


class TaskGraphFactory:
    @staticmethod
    def from_tasks(project_id: str, tasks) -> TaskGraph:
        graph = TaskGraph(project_id=project_id)

        for task in tasks:
            graph.add(
                TaskNode(
                    name=task["name"],
                    capability=task.get("capability", ""),
                    depends_on=list(task.get("depends_on", [])),
                )
            )

        return graph

    @staticmethod
    def from_project(project):
        previous = None

        for milestone in project.milestones:
            task = TaskNode(
                id=milestone.id,
                name=milestone.name,
            )

            if previous:
                task.depends_on.append(previous.id)

            milestone.tasks.append(task)
            previous = task

        return project
