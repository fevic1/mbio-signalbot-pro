class Composite:

    def __init__(self):
        self._children = []

    def add(self, child):
        self._children.append(child)
        return child

    def remove(self, child):
        if child in self._children:
            self._children.remove(child)

    def clear(self):
        self._children.clear()

    def __iter__(self):
        return iter(self._children)

    def __len__(self):
        return len(self._children)

    def execute(self, *args, **kwargs):
        result = None
        for child in self._children:
            if hasattr(child, "execute"):
                result = child.execute(*args, **kwargs)
            else:
                result = child(*args, **kwargs)
        return result
