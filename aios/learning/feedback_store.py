from aios.memory import EventStore, MemoryEvent


class FeedbackStore:

    def __init__(self):
        self.store = EventStore()

    def save(
        self,
        feedback,
    ):

        event = MemoryEvent(
            event_type="execution_feedback",
            action="feedback_recorded",
            source="aios_learning",
            metadata={
                "execution_id": feedback.execution_id,
                "success": feedback.success,
                "score": feedback.score,
                "observations": feedback.observations,
                "timestamp": feedback.timestamp,
            },
        )

        self.store.append(event)

        return event

    def all(self):

        return [
            event
            for event in self.store.all()
            if event.get("event_type")
            == "execution_feedback"
        ]
