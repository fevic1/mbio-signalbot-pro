from .models import CouncilIssue


class PlanValidator:
    REQUIRED_PHASES = {
        "research",
        "architecture",
        "implementation",
        "testing",
        "deployment",
        "monitoring",
    }

    def validate(self, plan):
        issues = []

        tasks = getattr(
            plan,
            "tasks",
            [
                task
                for milestone in getattr(
                    plan,
                    "milestones",
                    [],
                )
                for task in milestone.tasks
            ],
        )

        phase_ids = {task.id for task in tasks}

        missing = self.REQUIRED_PHASES - phase_ids

        for phase in sorted(missing):
            issues.append(CouncilIssue(
                code="missing_phase",
                severity="high",
                message=f"Missing required phase: {phase}",
            ))

        seen = set()
        for task in tasks:
            if task.id in seen:
                issues.append(CouncilIssue(
                    code="duplicate_task",
                    severity="medium",
                    message=f"Duplicate task id: {task.id}",
                ))
            seen.add(task.id)

        return issues

