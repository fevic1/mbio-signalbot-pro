from .models import Dependency
from ..models import TaskNode


class TaskGraphBuilder:

    def build(self, project):

        previous = None

        for milestone in project.milestones:

            task = TaskNode(
                id=milestone.id,
                name=milestone.name,
            )

            milestone.tasks.append(task)

            if previous:

                project.dependencies.append(
                    Dependency(
                        source=previous.id,
                        target=task.id,
                    )
                )

            previous = task

        return project
