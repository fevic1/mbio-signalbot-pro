from collections import deque


class Scheduler:
    """
    Converts an execution graph into runnable tasks.

    Only tasks whose dependencies are completed are
    placed into the execution queue.
    """

    def __init__(self, queue):
        self.queue = queue

    def initialize(self, graph):

        for task in graph.tasks:

            if not getattr(task, "depends_on", []):

                task.status = "READY"

                self.queue.push(task)

            else:

                task.status = "WAITING"

                self.queue.wait(task)

    def update(self):

        promoted = []

        waiting = deque()

        for task in self.queue.waiting:

            ready = True

            for dep in getattr(task, "depends_on", []):

                if getattr(dep, "status", None) != "COMPLETED":
                    ready = False
                    break

            if ready:

                task.status = "READY"

                self.queue.push(task)

                promoted.append(task)

            else:

                waiting.append(task)

        self.queue._waiting = waiting

        return promoted

    def has_work(self):

        return (
            len(self.queue.ready) > 0
            or len(self.queue.waiting) > 0
            or len(self.queue.running()) > 0
        )
