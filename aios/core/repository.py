class Repository:

    def __init__(self):
        self._items = {}

    def add(self, key, value):
        self._items[key] = value
        return value

    def get(self, key, default=None):
        return self._items.get(key, default)

    def remove(self, key):
        return self._items.pop(key, None)

    def all(self):
        return tuple(self._items.values())

    def keys(self):
        return tuple(self._items.keys())

    def clear(self):
        self._items.clear()

    def __len__(self):
        return len(self._items)
