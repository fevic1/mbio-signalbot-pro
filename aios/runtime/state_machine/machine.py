from datetime import datetime, timezone


class RuntimeStateMachine:

    def __init__(self, initial="created"):
        self._state = initial
        self._history = [
            {
                "state": initial,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        ]

    @property
    def state(self):
        return self._state

    def transition(self, new_state: str):
        self._state = new_state

        event = {
            "state": new_state,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._history.append(event)

        return event

    def history(self):
        return tuple(self._history)

    def reset(self, state="created"):
        self._state = state
        self._history.clear()

    def export(self):
        return {
            "current": self._state,
            "history": list(self._history),
        }
