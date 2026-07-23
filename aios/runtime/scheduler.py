from collections import deque


class TaskScheduler:

    def __init__(self):

        self.queue = deque()


    def enqueue_project(self, project):

        completed = set()

        while True:

            runnable = [
                d.target
                for d in project.dependencies
                if d.source in completed
            ]

            if not completed:

                runnable = [
                    project.milestones[0].tasks[0].id
                ]

            for task_id in runnable:

                if task_id not in self.queue:
                    self.queue.append(task_id)

            if not self.queue:
                break

            task = self.queue.popleft()

            yield task

            completed.add(task)
