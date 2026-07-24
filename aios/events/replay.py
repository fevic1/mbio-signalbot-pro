from pathlib import Path
import json


SAFE_REPLAY_EVENTS = {
    "trade_outcome",
    "execution_feedback",
    "optimizer_learning",
    "strategy_evaluation",
}


class EventReplay:

    def __init__(
        self,
        path=".aios/memory/events.json",
    ):

        self.path = Path(path)


    def load(self):

        if not self.path.exists():
            return []

        try:
            return json.loads(
                self.path.read_text()
            )

        except json.JSONDecodeError:
            return []


    def replay(
        self,
        handlers=None,
    ):

        handlers = handlers or {}

        replayed = 0

        for event in self.load():

            event_type = event.get(
                "event_type"
            )

            if event_type not in SAFE_REPLAY_EVENTS:
                continue


            handler = handlers.get(
                event_type
            )

            if handler:
                handler(event)

            replayed += 1


        return {
            "replayed": replayed,
            "available_events": len(self.load()),
        }
