from aios.events import Event, EventBus
from aios.learning import (
    LearningCoordinator,
    ProviderFeedbackHandler,
)
from aios.neural_proxy.intelligence import (
    ModelIntelligence,
)


bus = EventBus()

learning = LearningCoordinator()

intelligence = ModelIntelligence()


handler = ProviderFeedbackHandler(
    event_bus=bus,
    learning=learning,
    model_intelligence=intelligence,
)


bus.publish(
    Event(
        "model_execution.completed",
        "neural_proxy",
        {
            "provider": "openai",
            "model": "gpt-test",
            "capability": "research",
            "success": True,
        },
    )
)


profile = intelligence.profile(
    "gpt-test"
)


assert profile["provider"] == "openai"
assert profile["quality"] == "high"
assert profile["score"] == 10


assert len(
    learning.memory.history()
) == 1


print(
    "Provider feedback learning OK"
)
