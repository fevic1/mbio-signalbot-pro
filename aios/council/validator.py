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

        phase_ids = {task.id for task in plan.tasks}

        missing = self.REQUIRED_PHASES - phase_ids

        for phase in sorted(missing):
            issues.append(CouncilIssue(
                code="missing_phase",
                severity="high",
                message=f"Missing required phase: {phase}",
            ))

        seen = set()
        for task in plan.tasks:
            if task.id in seen:
                issues.append(CouncilIssue(
                    code="duplicate_task",
                    severity="medium",
                    message=f"Duplicate task id: {task.id}",
                ))
            seen.add(task.id)

        return issues

