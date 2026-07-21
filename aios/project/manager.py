from .models import Project, Goal


class ProjectManager:

    def create(self, title: str, description: str = "") -> Project:

        goal = Goal(
            id=title.lower().replace(" ", "-"),
            title=title,
            description=description,
        )

        return Project(
            goal=goal
        )
