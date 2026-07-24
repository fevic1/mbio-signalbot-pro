from typing import List, Dict


class GoalPlanner:


    def plan(
        self,
        goal,
    ) -> List[Dict]:

        objective = goal.objective


        tasks = [
            {
                "name": "analyze_objective",
                "description": (
                    f"Analyze requirements for: {objective}"
                ),
                "status": "pending",
            },
            {
                "name": "create_execution_plan",
                "description": (
                    "Create a structured execution plan"
                ),
                "status": "pending",
            },
            {
                "name": "execute_plan",
                "description": (
                    "Execute approved tasks"
                ),
                "status": "pending",
            },
            {
                "name": "review_result",
                "description": (
                    "Evaluate execution outcome"
                ),
                "status": "pending",
            },
        ]


        for task in tasks:
            goal.add_task(
                task
            )


        return tasks
