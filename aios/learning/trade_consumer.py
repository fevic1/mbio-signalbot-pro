from .trade_feedback import trade_to_feedback
from .optimizer import PlannerOptimizer
from aios.memory import EventStore


class TradeLearningConsumer:

    def __init__(self):

        self.store = EventStore()
        self.optimizer = PlannerOptimizer()


    def process(self):

        processed = 0

        for event in self.store.all():

            if event.get("event_type") != "trade_outcome":
                continue

            feedback = trade_to_feedback(
                event.get("metadata", {})
            )

            self.optimizer.update(
                feedback
            )

            processed += 1

        return processed
