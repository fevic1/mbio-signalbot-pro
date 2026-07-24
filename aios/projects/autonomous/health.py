from .models import ProjectHealth


class ProjectHealthMonitor:


    def analyze(
        self,
        project,
    ):

        milestones = getattr(
            project,
            "milestones",
            []
        )

        total = len(
            milestones
        )

        completed = 0

        issues = []

        recommendations = []


        for milestone in milestones:

            if isinstance(
                milestone,
                dict
            ):

                name = milestone.get(
                    "name"
                )

                status = milestone.get(
                    "status"
                )

            else:

                name = milestone.name

                status = milestone.status


            if status == "completed":

                completed += 1


            elif status == "blocked":

                issues.append(
                    {
                        "type":
                        "blocked_milestone",

                        "milestone":
                        name,
                    }
                )


        progress = (
            completed / total
            if total
            else 0
        )


        status = (
            "warning"
            if issues
            else "healthy"
        )


        if issues:

            recommendations.append(
                "Resolve blocked milestones"
            )


        return ProjectHealth(

            project_id=getattr(
                project,
                "id",
                "unknown"
            ),

            status=status,

            progress=progress,

            issues=issues,

            recommendations=recommendations,
        )
