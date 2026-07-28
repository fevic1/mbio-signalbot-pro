from collections import deque


class RuntimeQueue:

    def __init__(self):
        self._queue = deque()

    def push(self, item):
        self._queue.append(item)
        return item

    def pop(self):
        if not self._queue:
            return None

        return self._queue.popleft()

    def peek(self):
        if not self._queue:
            return None

        return self._queue[0]

    def clear(self):
        self._queue.clear()

    def items(self):
        return tuple(self._queue)

    def __len__(self):
        return len(self._queue)

    def __contains__(self, item):
        return item in self._queue
