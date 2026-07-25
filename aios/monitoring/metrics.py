from collections import defaultdict


class MetricsCollector:


    def __init__(self):

        self.counters = defaultdict(int)



    def increment(
        self,
        name,
        value=1,
    ):

        self.counters[name] += value



    def snapshot(self):

        return dict(
            self.counters
        )
