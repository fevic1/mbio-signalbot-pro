from .models import Milestone


class GoalDecomposer:

    def decompose(self, project):

        milestones = [
            Milestone(id="research", name="Research"),
            Milestone(id="architecture", name="Architecture"),
            Milestone(id="implementation", name="Implementation"),
            Milestone(id="testing", name="Testing"),
            Milestone(id="deployment", name="Deployment"),
            Milestone(id="monitoring", name="Monitoring"),
            Milestone(id="maintenance", name="Maintenance"),
        ]

        project.milestones = milestones

        return project
