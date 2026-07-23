from .context import ExecutionContext
from .blackboard import Blackboard
from .queue import ExecutionQueue
from .scheduler import Scheduler
from .dispatcher import Dispatcher
from .worker import Worker
from .monitor import ExecutionMonitor
from .checkpoint import CheckpointManager
from .recovery import RecoveryManager


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

            for capability in capabilities:
                self.queue.push(capability)

            while not self.queue.empty():

                ready = self.scheduler.next(
                    self.queue
                )

                if ready is None:
                    break

                agent_name = self.dispatcher.dispatch(
                    ready
                )

                output = self.worker.run(
                    agent_name,
                    context,
                )

                self.blackboard.store(
                    agent_name,
                    output,
                )

                context.add_result(
                    agent_name,
                    output,
                )

                self.monitor.record_success(
                    agent_name
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
