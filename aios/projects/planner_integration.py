from typing import Dict, List

from aios.projects import (
    Project,
)

from aios.projects.goal_link import GoalLinker

from aios.planning import (
    PlanningEngine,
    MilestoneGenerator,
    TaskGraphBuilder,
)


class ProjectPlanner:


    def __init__(
        self,
    ):

        self.planner = PlanningEngine()

        self.milestones = MilestoneGenerator()

        self.task_graph = TaskGraphBuilder()

        self.goal_linker = GoalLinker()



    def create_project_from_goal(
        self,
        project,
        goal,
    ):

        # Create execution plan

        plan = self.planner.create_plan(
            goal
        )


        # Generate milestones

        self.milestones.generate(
            plan
        )


        # Generate task dependency graph

        tasks = self.task_graph.build(
            plan.milestones
        )


        # Attach goal

        self.goal_linker.attach(
            project,
            goal
        )


        # Attach milestones

        for milestone in plan.milestones:

            project.add_milestone(
                milestone
            )


        return {
            "project": project,
            "plan": plan,
            "task_graph": tasks,
        }
