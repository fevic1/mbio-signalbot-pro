from .manager import GoalManager
from aios.project.manager import ProjectManager


class GoalEngine:

    def __init__(
        self,
        manager=None,
        project_manager=None,
    ):

        self.manager = manager or GoalManager()
        self.project_manager = project_manager or ProjectManager()


    def submit(
        self,
        objective,
        constraints=None,
        priority=1,
    ):

        goal = self.manager.create(
            objective=objective,
            constraints=constraints,
            priority=priority,
        )

        return self.project_manager.create(goal)
