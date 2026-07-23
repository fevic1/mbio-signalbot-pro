from aios.orchestrator import AIOSOrchestrator
from aios.system.system import AIOSSystem

from aios.project import ProjectManager
from aios.council import CouncilManager

from aios.execution import ExecutionPlanner
from aios.capabilities.health import CapabilityHealthManager

from aios.registry import CapabilityRegistry
from aios.runtime import TaskManager
from aios.events import EventBus

from aios.bootstrap import CapabilityBootstrap

from aios.governance import (
    ApprovalManager,
    AuditLogger,
)

from aios.decision import (
    DecisionEngine,
    DecisionPolicy,
)

from aios.workflows.decision_workflow import DecisionWorkflow

from aios.workflows import (
    WorkflowEngine,
    MultiAgentWorkflow,
)


class SystemBootstrap:

    def __init__(self, memory=None):
        self.memory = memory

    def boot(self):

        registry = CapabilityRegistry()
        task_manager = TaskManager()
        approval = ApprovalManager()
        audit = AuditLogger()
        event_bus = EventBus()
        execution_planner = ExecutionPlanner()
        capability_health = CapabilityHealthManager()

        CapabilityBootstrap(
            registry=registry,
            memory=self.memory,
        ).load_capabilities()

        decision = DecisionEngine(
            approval_manager=approval,
            audit=audit,
            event_bus=event_bus,
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

        system.capability_health = capability_health

        system.council = CouncilManager()
        system.project_manager = ProjectManager()
        system.decision_policy = DecisionPolicy()

        system.orchestrator = AIOSOrchestrator(system)

        system.workflow_engine = WorkflowEngine(system)

        system.multi_agent_workflow = MultiAgentWorkflow(system)

        system.decision_workflow = DecisionWorkflow(system)

        # inject council into workflow
        system.decision_workflow.council = system.council

        return system
