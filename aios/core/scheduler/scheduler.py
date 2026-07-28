class Scheduler:

    def __init__(self):
        self._tasks = []

    def add(self, task):
        self._tasks.append(task)
        return task

    def remove(self, task):
        if task in self._tasks:
            self._tasks.remove(task)

    def clear(self):
        self._tasks.clear()

    def run(self, *args, **kwargs):
        result = None
        for task in self._tasks:
            if hasattr(task, "execute"):
                result = task.execute(*args, **kwargs)
            else:
                result = task(*args, **kwargs)
        return result

    def __iter__(self):
        return iter(self._tasks)
