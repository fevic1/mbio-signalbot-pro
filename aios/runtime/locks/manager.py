from threading import RLock


class RuntimeLockManager:

    def __init__(self):
        self._locks: dict[str, RLock] = {}

    def create(self, name: str):
        if name not in self._locks:
            self._locks[name] = RLock()

        return self._locks[name]

    def acquire(self, name: str):
        lock = self.create(name)
        lock.acquire()
        return lock

    def release(self, name: str):
        lock = self._locks.get(name)

        if lock:
            lock.release()

    def exists(self, name: str):
        return name in self._locks

    def names(self):
        return tuple(sorted(self._locks))

    def clear(self):
        self._locks.clear()

    def __len__(self):
        return len(self._locks)
