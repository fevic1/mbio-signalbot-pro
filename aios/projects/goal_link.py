from typing import Dict


class GoalLinker:


    def attach(
        self,
        project,
        goal,
    ):

        goal_data = {
            "id": goal.id,
            "objective": goal.objective,
            "priority": goal.priority,
            "status": goal.status,
        }


        project.add_goal(
            goal_data
        )


        return project
