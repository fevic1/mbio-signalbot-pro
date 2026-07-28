class Session:

    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        return value

    def update(self, **kwargs):
        self._data.update(kwargs)

    def clear(self):
        self._data.clear()

    def snapshot(self):
        return dict(self._data)

    def restore(self, snapshot):
        self._data = dict(snapshot)
        return self
