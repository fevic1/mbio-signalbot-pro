class Context:

    def __init__(self):
        self._values = {}

    def get(self, key, default=None):
        return self._values.get(key, default)

    def set(self, key, value):
        self._values[key] = value
        return value

    def update(self, **kwargs):
        self._values.update(kwargs)

    def clear(self):
        self._values.clear()

    def copy(self):
        c = Context()
        c._values = dict(self._values)
        return c

    def as_dict(self):
        return dict(self._values)
