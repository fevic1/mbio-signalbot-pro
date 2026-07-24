from aios.goals import GoalPlanner
from aios.executive.context import ExecutiveContext
from aios.executive.capability_matcher import CapabilityMatcher


class ExecutiveLoop:


    def __init__(
        self,
        skill_manager,
    ):

        self.skill_manager = skill_manager

        self.planner = GoalPlanner()

        self.matcher = CapabilityMatcher(
            skill_manager
        )


    def start(
        self,
        goal,
        permissions=None,
    ):

        tasks = self.planner.plan(
            goal
        )


        capability_result = (
            self.matcher.match(goal)
        )


        context = ExecutiveContext(
            goal_id=goal.id,
            objective=goal.objective,
            permissions=(
                permissions.allowed_actions()
                if permissions
                else {}
            ),
        )


        context.execution_plan = tasks


        context.selected_skills = [
            item["skill"]
            for item
            in capability_result["matched_skills"]
        ]


        return context
