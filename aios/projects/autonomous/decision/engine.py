from .models import ProjectDecision


class ProjectDecisionEngine:


    def decide(
        self,
        health,
    ):

        decisions = []


        for issue in health.issues:

            if (
                issue.get("type")
                ==
                "blocked_milestone"
            ):

                decisions.append(
                    ProjectDecision(
                        action=
                        "resolve_blocked_milestone",

                        reason=
                        f"Milestone blocked: "
                        f"{issue.get('milestone')}",

                        priority=
                        "high",

                        metadata={
                            "milestone":
                            issue.get(
                                "milestone"
                            )
                        },
                    )
                )


        if not decisions:

            decisions.append(
                ProjectDecision(
                    action=
                    "continue_execution",

                    reason=
                    "Project operating normally",

                    priority=
                    "normal",
                )
            )


        return decisions
