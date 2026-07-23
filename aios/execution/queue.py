from collections import deque


class ExecutionQueue:

    def __init__(self):
        self._ready = deque()
        self._waiting = deque()
        self._running = {}
        self._failed = deque()
        self._finished = deque()

    # ---------- READY ----------

    def push(self, task):
        self._ready.append(task)

    def pop(self):
        if not self._ready:
            return None

        task = self._ready.popleft()
        self._running[task.id] = task
        return task

    # ---------- WAITING ----------

    def wait(self, task):
        self._waiting.append(task)

    # ---------- RUNNING ----------

    def running(self):
        return list(self._running.values())

    # ---------- FINISHED ----------

    def finish(self, task):
        self._running.pop(task.id, None)
        self._finished.append(task)

    # ---------- FAILED ----------

    def fail(self, task):
        self._running.pop(task.id, None)
        self._failed.append(task)

    def retry(self, task):

        try:
            self._failed.remove(task)
        except ValueError:
            return False

        self._ready.appendleft(task)
        return True

    # ---------- CANCEL ----------

    def cancel(self, task_id):

        self._ready = deque(
            t for t in self._ready
            if t.id != task_id
        )

        self._waiting = deque(
            t for t in self._waiting
            if t.id != task_id
        )

        self._running.pop(task_id, None)

    # ---------- PRIORITY ----------

    def prioritize(self, task):

        try:
            self._ready.remove(task)
        except ValueError:
            return False

        self._ready.appendleft(task)
        return True

    # ---------- STATUS ----------

    @property
    def ready(self):
        return list(self._ready)

    @property
    def waiting(self):
        return list(self._waiting)

    @property
    def failed(self):
        return list(self._failed)

    @property
    def finished(self):
        return list(self._finished)

    def empty(self):
        return (
            not self._ready
            and not self._waiting
            and not self._running
        )
