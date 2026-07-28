from aios.core.identifiable import Identifiable

from aios.core.factory import Factory

from aios.goals.models import Goal
from .models import Project
from .planner import ProjectPlanner


class ProjectManager(Identifiable):

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
