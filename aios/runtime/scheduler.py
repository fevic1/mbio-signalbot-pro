from collections import deque


class TaskScheduler:

    def __init__(self):
        self.queue = deque()

    def enqueue_project(self, project):

        tasks = []

        for milestone in project.milestones:
            tasks.extend(milestone.tasks)

        completed = set()

        while tasks:

            runnable = [
                task
                for task in tasks
                if task.id not in completed
                and all(
                    dependency in completed
                    for dependency in getattr(
                        task,
                        "depends_on",
                        [],
                    )
                )
            ]

            if not runnable:
                break

            for task in runnable:
                if task.id not in self.queue:
                    self.queue.append(task.id)

            while self.queue:
                task_id = self.queue.popleft()

                yield task_id

                completed.add(task_id)
