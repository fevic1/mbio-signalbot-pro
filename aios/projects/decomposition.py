from .milestones import Milestone


class ProjectDecomposer:


    def decompose(
        self,
        project,
        objective,
    ):

        phases = []


        text = objective.lower()


        if any(
            word in text
            for word in [
                "build",
                "create",
                "develop",
            ]
        ):

            phases = [
                (
                    "Research",
                    "Understand requirements and constraints",
                ),
                (
                    "Architecture",
                    "Design system structure",
                ),
                (
                    "Development",
                    "Implement required components",
                ),
                (
                    "Testing",
                    "Validate functionality and quality",
                ),
                (
                    "Deployment",
                    "Release operational system",
                ),
                (
                    "Monitoring",
                    "Track health and improve",
                ),
            ]


        else:

            phases = [
                (
                    "Analysis",
                    "Analyze objective",
                ),
                (
                    "Execution",
                    "Execute planned work",
                ),
                (
                    "Review",
                    "Evaluate outcome",
                ),
            ]


        for name, description in phases:

            project.add_milestone(
                Milestone(
                    name=name,
                    description=description,
                ).describe()
            )


        return project
