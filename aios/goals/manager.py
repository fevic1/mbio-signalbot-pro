from .models import Goal


class GoalManager:

    def __init__(self):

        self.goals = {}


    def create(
        self,
        objective,
        constraints=None,
        priority=1,
    ):

        goal = Goal(
            objective=objective,
            constraints=constraints or [],
            priority=priority,
        )

        self.goals[
            goal.id
        ] = goal

        return goal


    def get(
        self,
        goal_id,
    ):

        return self.goals.get(
            goal_id
        )


    def update_status(
        self,
        goal_id,
        status,
    ):

        goal = self.get(
            goal_id
        )

        if goal:

            goal.status = status

        return goal


    def list(self):

        return list(
            self.goals.values()
        )
