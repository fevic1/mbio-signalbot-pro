from aios.capabilities.executor import CapabilityExecutor


class Worker:


    def __init__(
        self,
        system,
        blackboard,
        queue,
    ):

        self.system = system
        self.blackboard = blackboard
        self.queue = queue
        self.executor = CapabilityExecutor()



    def execute(
        self,
        task,
        context,
    ):

        capability = task.capability


        result = self.executor.execute(
            capability
        )


        output = {

            "capability": capability,

            "provider":
                result.provider,

            "model":
                result.model,

            "content":
                result.content,

        }


        self.blackboard.store(
            task.id,
            output,
        )


        self.queue.finish(
            task
        )


        return output
