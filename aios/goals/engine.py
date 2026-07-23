from .manager import GoalManager


class GoalEngine:

    def __init__(
        self,
        manager=None,
    ):

        self.manager = manager or GoalManager()


    def submit(
        self,
        objective,
        constraints=None,
        priority=1,
    ):

        return self.manager.create(
            objective,
            constraints,
            priority,
        )
