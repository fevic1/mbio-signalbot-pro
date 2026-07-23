from datetime import datetime


class AIOSKernel:

    def __init__(
        self,
        registry=None,
        task_manager=None,
        memory=None,
        governance=None,
        bootstrap=None
    ):

        self.registry = registry
        self.task_manager = task_manager
        self.memory = memory
        self.governance = governance
        self.bootstrap = bootstrap

        self.status = "initialized"


    def start(self):

        if self.bootstrap:

            self.bootstrap.load_capabilities()


        self.status = "running"


        return {
            "status": self.status,
            "time": datetime.utcnow().isoformat()
        }


    def health(self):

        return {

            "status": self.status,

            "agents":
                len(
                    self.registry.agents
                )
                if self.registry
                else 0,

            "tasks":
                len(
                    self.task_manager.tasks
                )
                if self.task_manager
                else 0
        }
