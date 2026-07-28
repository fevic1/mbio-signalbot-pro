class ExecutionEngine:

    def __init__(self):
        self._steps = []

    def add(self, step):
        self._steps.append(step)
        return step

    def extend(self, steps):
        self._steps.extend(steps)

    def clear(self):
        self._steps.clear()

    def __iter__(self):
        return iter(self._steps)

    def __len__(self):
        return len(self._steps)

    def run(self, context=None):
        result = context
        for step in self._steps:
            if hasattr(step, "execute"):
                result = step.execute(result)
            else:
                result = step(result)
        return result
