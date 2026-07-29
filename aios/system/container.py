class AIOSContainer:


    def __init__(self):

        self.services = {}



    def register(
        self,
        name,
        service,
    ):

        self.services[name] = service



    def get(
        self,
        name,
    ):

        return self.services.get(
            name
        )



    def describe(
        self,
    ):

        return list(
            self.services.keys()
        )


    def __getitem__(self, name):
        return self.services[name]


    def status(self):
        return {
            "services": list(self.services.keys()),
            "count": len(self.services),
        }


    @property
    def orchestrator(self):
        return self.services.get("orchestrator")


    @property
    def task_manager(self):
        return self.services.get("task_manager")


    @property
    def multi_agent_workflow(self):
        return self.services.get("multi_agent_workflow")


    @property
    def audit_logger(self):
        return self.services.get("audit_logger")


    @property
    def decision_engine(self):
        return self.services.get("decision_engine")

    @property
    def neural_proxy(self):
        return self.services.get("neural_proxy")


    @property
    def capability_registry(self):
        return self.services.get("capability_registry")


    @property
    def capability_health(self):
        return self.services.get("capability_health")

    @property
    def event_bus(self):
        return self.services.get("event_bus")

    @property
    def skill_registry(self):
        return self.services.get("skill_registry")


    @property
    def model_registry(self):
        return self.services.get("model_registry")


    @property
    def llm_router(self):
        return self.services.get("llm_router")


    @property
    def memory_manager(self):
        return self.services.get("memory_manager")


    @property
    def decision_workflow(self):
        return self.services.get("decision_workflow")


    @property
    def workflow_engine(self):
        return self.services.get("workflow_engine")


    @property
    def execution_planner(self):
        return self.services.get("execution_planner")
