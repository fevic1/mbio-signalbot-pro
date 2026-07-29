from aios.core.execution import ExecutionEngine

from .assignment import (
    TaskAssignmentEngine,
)

from .mission_executor import (
    MissionExecutor,
)


class ExecutionOrchestrator:


    def __init__(
        self,
        event_bus=None,
        governance=None,
    ):

        self.governance = governance

        self.assignment = (
            TaskAssignmentEngine()
        )

        self.executor = MissionExecutor(
            event_bus=event_bus
        )



    def run_mission(
        self,
        task_graph,
        mission_team,
        approval_id=None,
    ):


        assignments = (
            self.assignment.assign(
                task_graph,
                mission_team,
            )
        )


        if self.governance:

            if approval_id:

                approval = (
                    self.governance
                    .approval_manager
                    .get(approval_id)
                )

                if not approval or approval["status"] != "approved":

                    return {
                        "assignments": assignments,
                        "results": [],
                        "governance": {
                            "allowed": False,
                            "status": (
                                approval["status"]
                                if approval
                                else "missing"
                            ),
                            "approval_id": approval_id,
                        },
                    }

            else:

                decision = self.governance.request(
                    action="execute_mission",
                    agent="execution_orchestrator",
                    permission="execute",
                    payload={
                        "assignments": assignments,
                    },
                )

                if not decision["allowed"]:
                    return {
                        "assignments": assignments,
                        "results": [],
                        "governance": decision,
                    }


        results = (
            self.executor.execute(
                assignments
            )
        )


        return {
            "assignments": assignments,
            "results": results,
        }
