from ..models import TaskNode


class TaskGraphBuilder:

    def build(self, project):

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
