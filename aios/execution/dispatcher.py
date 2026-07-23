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
        return self.queue.pop()

    async def dispatch(self, worker) -> bool:
        task = self.next()

        if task is None:
            return False

        await worker.execute(task)
        return True

    async def drain(self, worker) -> int:
        dispatched = 0

        while await self.dispatch(worker):
            dispatched += 1

        return dispatched
