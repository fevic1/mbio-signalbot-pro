from typing import Any


class Pipeline:

    def __init__(self):
        self._stages = []

    def add_stage(self, stage):
        self._stages.append(stage)
        return stage

    def extend(self, stages):
        self._stages.extend(stages)

    def execute(self, value: Any = None):
        result = value
        for stage in self._stages:
            if hasattr(stage, "execute"):
                result = stage.execute(result)
            else:
                result = stage(result)
        return result

    def clear(self):
        self._stages.clear()

    def __iter__(self):
        return iter(self._stages)
