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
    ):

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
    ):


        assignments = (
            self.assignment.assign(
                task_graph,
                mission_team,
            )
        )


        results = (
            self.executor.execute(
                assignments
            )
        )


        return {
            "assignments": assignments,
            "results": results,
        }
