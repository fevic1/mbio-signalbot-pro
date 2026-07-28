#!/usr/bin/env python3

from threading import RLock
from collections import defaultdict


class Metrics:

    def __init__(self):
        self._lock = RLock()
        self._counters = defaultdict(int)
        self._gauges = {}
        self._timers = defaultdict(list)

    def inc(self, name, value=1):
        with self._lock:
            self._counters[name] += value

    def gauge(self, name, value):
        with self._lock:
            self._gauges[name] = value

    def timing(self, name, seconds):
        with self._lock:
            self._timers[name].append(seconds)

    def snapshot(self):
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timers": {
                    k: {
                        "count": len(v),
                        "avg": (sum(v) / len(v)) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                    }
                    for k, v in self._timers.items()
                }
            }


metrics = Metrics()


if __name__ == "__main__":

    metrics.inc("plugins.loaded")
    metrics.inc("plugins.loaded")
    metrics.gauge("services", 19)
    metrics.timing("boot", 0.18)
    metrics.timing("boot", 0.22)

    print(metrics.snapshot())
