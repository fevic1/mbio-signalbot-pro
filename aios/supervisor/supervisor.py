from .models import SupervisorReport


class AutonomousSupervisor:


    def __init__(
        self,
        project_manager,
    ):

        self.project_manager = project_manager



    def check_projects(
        self,
        projects,
    ):

        issues = []

        actions = []


        for project in projects:

            result = (
                self.project_manager
                .evaluate(project)
            )


            health = result.health


            if (
                health["status"]
                !=
                "healthy"
            ):

                issues.append(
                    health
                )


            actions.extend(
                result.actions
            )


        return SupervisorReport(

            checked_projects=len(
                projects
            ),

            issues=issues,

            actions=actions,
        )
