from .context import ExecutionContext
from .blackboard import Blackboard
from .queue import ExecutionQueue
from .scheduler import Scheduler
from .dispatcher import Dispatcher
from .worker import Worker
from .monitor import ExecutionMonitor
from .checkpoint import CheckpointManager
from .recovery import RecoveryManager
from .task import CapabilityTask
from aios.agents.factory import AgentFactory


class ExecutionExecutor:

    def __init__(
        self,
        system,
        planner,
    ):
        self.system = system
        self.planner = planner

        self.blackboard = Blackboard()
        self.queue = ExecutionQueue()
        self.scheduler = Scheduler()
        self.dispatcher = Dispatcher()
        self.worker = Worker(system, self.blackboard, self.queue)
        self.agent_factory = AgentFactory(system.capability_registry)
        self.monitor = ExecutionMonitor()
        self.checkpoint = CheckpointManager()
        self.recovery = RecoveryManager()

    def execute(
        self,
        task,
    ):

        context = ExecutionContext(
            task,
            event_bus=self.system.event_bus,
        )

        context.start()

        try:

            capabilities = self.planner.get_capabilities(task["category"])

            workers = self.agent_factory.create(
                capabilities
            )

            for worker in workers:
                self.queue.push(
                    CapabilityTask(worker)
                )

            while not self.queue.empty():

                ready = self.scheduler.next(
                    self.queue
                )

                if ready is None:
                    break

                task_result = self.worker.execute(
                    ready
                )

                output = task_result

                capability = ready.worker.capability

                self.blackboard.store(
                    capability,
                    output,
                )

                context.add_result(
                    capability,
                    output,
                )

                context.set_metadata(
                    f"capability:{capability}",
                    {
                        "provider": output.get("provider"),
                        "model": output.get("model"),
                        "latency": output.get("latency"),
                        "cost": output.get("cost"),
                    },
                )

                self.monitor.record_success(
                    capability
                )

                self.checkpoint.save(
                    context
                )

            context.complete()

            if self.system.decision_workflow:

                decision = self.system.decision_workflow.run(
                    task,
                    context,
                )

                context.set_metadata(
                    "decision",
                    decision,
                )

        except Exception as error:

            self.monitor.record_failure(
                str(error)
            )

            self.recovery.handle(
                error,
                context,
            )

            context.fail(error)
            raise

        return context
