class AIOSSystem:

    def __init__(
        self,
        registry,
        task_manager,
        approval_manager,
        audit_logger,
        decision_engine,
        memory_manager=None,
        orchestrator=None,
        event_bus=None,
        execution_planner=None,
    ):

        self.registry = registry

        self.task_manager = task_manager

        self.approval_manager = approval_manager

        self.audit_logger = audit_logger

        self.decision_engine = decision_engine

        self.memory_manager = memory_manager

        self.orchestrator = orchestrator

        self.event_bus = event_bus

        self.execution_planner = execution_planner

        self.decision_history = []

        self.workflow_engine = None

        self.multi_agent_workflow = None

        self.decision_workflow = None

        self.project_manager = None

    def status(self):

        return {

            "agents":
                len(
                    self.registry.list()
                ),

            "tasks":
                len(
                    self.task_manager.list_tasks()
                ),

            "memory":
                self.memory_manager is not None,

            "orchestrator":
                self.orchestrator is not None,

            "event_bus":
                self.event_bus is not None,
        }
