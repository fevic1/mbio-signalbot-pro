from aios.orchestrator import AIOSOrchestrator
from aios.system.system import AIOSSystem

from aios.execution import ExecutionPlanner

from aios.registry import AgentRegistry
from aios.runtime import TaskManager
from aios.events import EventBus

from aios.bootstrap import AgentBootstrap

from aios.governance import (
    ApprovalManager,
    AuditLogger,
)

from aios.decision import DecisionEngine

from aios.workflows.decision_workflow import DecisionWorkflow

from aios.workflows import (
    WorkflowEngine,
    MultiAgentWorkflow,
)


class SystemBootstrap:

    def __init__(
        self,
        memory=None,
    ):

        self.memory = memory


    def boot(self):

        registry = AgentRegistry()

        task_manager = TaskManager()

        approval = ApprovalManager()

        audit = AuditLogger()

        event_bus = EventBus()

        execution_planner = ExecutionPlanner()


        AgentBootstrap(
            registry=registry,
            memory=self.memory,
        ).load_agents()


        decision = DecisionEngine(
            approval_manager=approval,
            audit=audit,
        )


        system = AIOSSystem(
            event_bus=event_bus,
            registry=registry,
            task_manager=task_manager,
            approval_manager=approval,
            audit_logger=audit,
            decision_engine=decision,
            memory_manager=self.memory,
            execution_planner=execution_planner,
        )


        # Core services

        system.orchestrator = AIOSOrchestrator(
            system
        )

        system.workflow_engine = WorkflowEngine(
            system
        )

        system.multi_agent_workflow = MultiAgentWorkflow(
            system
        )

        system.decision_workflow = DecisionWorkflow(
            system
        )


        return system
