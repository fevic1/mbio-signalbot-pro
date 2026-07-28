from typing import Any


class Workflow:

    def __init__(self):
        self.steps = []

    def add_step(self, step):
        self.steps.append(step)
        return step

    def execute(self, context: Any = None):
        result = context
        for step in self.steps:
            if hasattr(step, "execute"):
                result = step.execute(result)
            else:
                result = step(result)
        return result
