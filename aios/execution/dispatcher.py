from typing import Optional


class Dispatcher:
    """
    Chooses the next executable task from the queue.

    The scheduler decides *when* tasks become ready.
    The dispatcher decides *which* ready task to execute next.
    """

    def __init__(self, queue):
        self.queue = queue

    def next(self) -> Optional[object]:
        """
        Returns the next executable task.
        """
        return self.queue.pop()

    def dispatch(self, worker) -> bool:
        """
        Sends one task to a worker.

        Returns
        -------
        True  -> task dispatched
        False -> queue empty
        """
        task = self.next()

        if task is None:
            return False

        worker.execute(task)

        return True

    def drain(self, worker):
        """
        Executes until the ready queue is empty.
        """
        while self.dispatch(worker):
            pass
