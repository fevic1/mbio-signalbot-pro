#!/usr/bin/env python3

from collections import defaultdict


class Pipeline:

    def __init__(self):
        self._pipelines = defaultdict(list)

    def register(self, name, stage):
        self._pipelines[name].append(stage)

    def execute(self, name, data):

        result = data

        for stage in self._pipelines.get(name, []):
            result = stage(result)

        return result

    def list(self):
        return {
            name: len(stages)
            for name, stages in self._pipelines.items()
        }


pipeline = Pipeline()


if __name__ == "__main__":

    def uppercase(x):
        return x.upper()

    def suffix(x):
        return x + "!"

    pipeline.register("demo", uppercase)
    pipeline.register("demo", suffix)

    print(pipeline.execute("demo", "aios"))
    print(pipeline.list())
