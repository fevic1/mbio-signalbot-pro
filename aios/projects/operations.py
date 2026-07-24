from datetime import datetime, timezone


class ProjectOperationsManager:


    def inspect(
        self,
        project,
    ):

        issues = []

        completed = 0
        total = len(
            project.milestones
        )


        for milestone in project.milestones:

            status = milestone.get(
                "status"
            )


            if status == "blocked":

                issues.append(
                    {
                        "type": "blocked_milestone",
                        "milestone": milestone.get(
                            "name"
                        ),
                    }
                )


            if status == "completed":

                completed += 1



        progress = 0

        if total:

            progress = (
                completed / total
            )


        health = "healthy"


        if issues:

            health = "warning"


        if project.status == "blocked":

            health = "critical"



        return {
            "project": project.name,
            "status": project.status,
            "health": health,
            "progress": progress,
            "issues": issues,
            "checked_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        }



    def update_status(
        self,
        project,
        status,
    ):

        allowed = [
            "created",
            "planning",
            "active",
            "blocked",
            "review",
            "completed",
            "archived",
        ]


        if status not in allowed:

            raise ValueError(
                f"Invalid project status: {status}"
            )


        project.status = status

        return project



    def find_blockers(
        self,
        project,
    ):

        blockers = []


        for milestone in project.milestones:

            if milestone.get(
                "status"
            ) == "blocked":

                blockers.append(
                    milestone
                )


        return blockers
