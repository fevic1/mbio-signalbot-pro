from .models import Project, Goal
from .planner import ProjectPlanner


class ProjectManager:

    def __init__(self):
        self.planner = ProjectPlanner()

    def create(self, title: str, description: str = "") -> Project:

        goal = Goal(
            id=title.lower().replace(" ", "-"),
            title=title,
            description=description,
        )

        project = Project(
            goal=goal,
        )

        return self.planner.generate(project)
