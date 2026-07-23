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
from aios.capabilities.factory import CapabilityFactory


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
        self.scheduler = Scheduler(self.queue)
        self.dispatcher = Dispatcher(self.queue)
        self.worker = Worker(
            system,
            self.blackboard,
            self.queue,
        )
        self.capability_factory = CapabilityFactory(
            system,
            system.capability_registry
        )
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

        self.worker.bind(
            context
        )

        try:

            plan = self.planner.resolve(
                self.system,
                task["category"],
            )

            if plan["type"] == "skill":
                plan["target"].execute(context)
            else:
                workers = self.capability_factory.create(
                    plan["target"]
                )

                for worker in workers:
                    self.queue.push(
                        CapabilityTask(worker)
                    )

            while True:

                if not self.dispatcher.dispatch(
                    self.worker
                ):
                    break

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
