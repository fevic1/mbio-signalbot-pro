from typing import Dict


class GoalManager:


    def __init__(self):

        self.goals: Dict = {}


    def register(
        self,
        goal,
    ):

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


    def active(
        self,
    ):

        return [
            goal
            for goal in self.goals.values()
            if goal.status == "active"
        ]


    def summary(
        self,
    ):

        return [
            goal.describe()
            for goal in self.goals.values()
        ]
