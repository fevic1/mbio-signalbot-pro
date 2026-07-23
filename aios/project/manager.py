from aios.goals.models import Goal
from .models import Project
from .planner import ProjectPlanner


class ProjectManager:

    def __init__(self):

        self.planner = ProjectPlanner()


    def create(
        self,
        goal: Goal,
    ) -> Project:

        project = Project(
            goal=goal,
        )

        return self.planner.generate(project)
