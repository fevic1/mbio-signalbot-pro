from datetime import datetime


class AIOSOrchestrator:

    def __init__(
        self,
        system=None,
        task_manager=None,
        registry=None,
        decision_engine=None,
        workflow_engine=None,
    ):

        if system is None:
            class CompatibilitySystem:
                pass

            system = CompatibilitySystem()

            system.task_manager = task_manager
            system.registry = registry
            system.decision_engine = decision_engine
            system.workflow_engine = workflow_engine

        self.system = system


    def status(self):

        return {
            "status": "running",
            "time": datetime.utcnow().isoformat(),
            "agents": len(
                self.system.registry.list()
            ),
            "tasks": len(
                self.system.task_manager.list_tasks()
            ),
            "decision_engine":
                self.system.decision_engine is not None,
        }


    def submit_task(
        self,
        name,
        category,
        priority="normal"
    ):

        return self.system.task_manager.create_task(
            name=name,
            category=category,
            priority=priority,
        )


    def assign_agent(
        self,
        task_id,
        agent_name
    ):

        return self.system.task_manager.assign(
            task_id,
            agent_name,
        )


    async def execute_task(
        self,
        task_id
    ):

        task = self.system.task_manager.get_task(
            task_id
        )

        if task is None:
            raise ValueError(
                "Task not found"
            )


        if not task["assigned_agent"]:

            raise ValueError(
                "Task has no assigned agent"
            )


        result = await self.system.workflow_engine.execute(
            task
        )


        return result



    def execute_decision(
        self,
        proposal,
        deliberation,
    ):

        if self.system.decision_engine is None:

            raise RuntimeError(
                "Decision engine unavailable"
            )


        decision = self.system.decision_engine.decide(
            proposal,
            deliberation,
        )


        return decision
