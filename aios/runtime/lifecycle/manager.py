from .events import LifecycleEvent, LifecyclePhase


class LifecycleManager:

    def __init__(self):
        self._events: list[LifecycleEvent] = []

    def emit(self, phase: LifecyclePhase, component: str):
        event = LifecycleEvent(phase, component)
        self._events.append(event)
        return event

    def history(self):
        return tuple(self._events)

    def latest(self):
        return self._events[-1] if self._events else None

    def clear(self):
        self._events.clear()
