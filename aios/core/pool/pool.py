class Pool:

    def __init__(self):
        self._objects = []

    def acquire(self):
        return self._objects.pop() if self._objects else None

    def release(self, obj):
        self._objects.append(obj)

    def add(self, obj):
        self._objects.append(obj)
        return obj

    def clear(self):
        self._objects.clear()

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)
