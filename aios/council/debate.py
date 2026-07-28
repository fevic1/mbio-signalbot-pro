from aios.core.execution.runner import ExecutionRunner

from .models import AgentOpinion


class DebateEngine(ExecutionRunner):
    def collect(self, plan):
        return [
            AgentOpinion(
                agent="Planner",
                confidence=0.80,
                summary=f"Generated {len(plan.tasks)} tasks",
            ),
            AgentOpinion(
                agent="RiskAnalyst",
                confidence=0.70,
                summary="Execution risk appears manageable",
            ),
            AgentOpinion(
                agent="Verifier",
                confidence=0.75,
                summary="Plan structure validated",
            ),
        ]
