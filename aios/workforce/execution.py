from aios.core.execution.runner import ExecutionRunner

from aios.core.execution import ExecutionEngine

from .contracts import (
    AgentTask,
    AgentResult,
)


class AgentExecutor(ExecutionRunner):


    def execute(
        self,
        agent,
        task: AgentTask,
    ):

        # Placeholder execution boundary.
        #
        # Real execution will later route through:
        # - LLM providers
        # - tools
        # - skills
        # - verification


        return AgentResult(
            agent=agent.name,
            status="completed",
            output={
                "task": task.task.get(
                    "name"
                )
            },
            evidence=[
                "task accepted by agent contract"
            ],
            confidence=0.5,
        )
