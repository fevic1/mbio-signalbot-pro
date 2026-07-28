from collections import deque


class Queue:

    def __init__(self):
        self._queue = deque()

    def push(self, item):
        self._queue.append(item)
        return item

    def pop(self):
        return self._queue.popleft()

    def peek(self):
        return self._queue[0] if self._queue else None

    def clear(self):
        self._queue.clear()

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return iter(self._queue)
