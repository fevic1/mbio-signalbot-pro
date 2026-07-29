import asyncio

from aios.events import EventBus
from aios.events.models import AIOSDomainEvent
from aios.learning import LearningCoordinator, ProviderFeedbackHandler


def test_model_execution_feedback_reaches_learning_memory():

    bus = EventBus()

    learning = LearningCoordinator()

    ProviderFeedbackHandler(
        event_bus=bus,
        learning=learning,
    )

    bus.publish(
        AIOSDomainEvent(
            "model_execution.completed",
            source="test",
            payload={
                "provider": "openai",
                "model": "gpt-test",
                "capability": "research",
                "success": True,
            },
        )
    )

    records = learning.memory.history()

    assert len(records) == 1

    execution = records[0]["execution"]["result"]

    assert execution["type"] == "model_execution"
    assert execution["provider"] == "openai"
    assert execution["model"] == "gpt-test"
