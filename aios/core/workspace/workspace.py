class Workspace:

    def __init__(self):
        self._state = {}

    def get(self, key, default=None):
        return self._state.get(key, default)

    def set(self, key, value):
        self._state[key] = value
        return value

    def update(self, **kwargs):
        self._state.update(kwargs)

    def clear(self):
        self._state.clear()

    def snapshot(self):
        return dict(self._state)
