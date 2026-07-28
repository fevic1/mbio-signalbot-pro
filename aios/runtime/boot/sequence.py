
class RuntimeBootSequence:

    def __init__(self, kernel):
        self.kernel = kernel

    def register_defaults(self):
        self.kernel.bootstrap_graph.register(
            "workflow_engine",
            lambda: self.kernel.workflow_engine
        )

        self.kernel.bootstrap_graph.register(
            "task_engine",
            lambda: self.kernel.task_engine
        )

        self.kernel.bootstrap_graph.register(
            "execution_graph",
            lambda: self.kernel.execution_graph
        )

        self.kernel.bootstrap_graph.register(
            "tool_registry",
            lambda: self.kernel.tool_registry
        )

        self.kernel.bootstrap_graph.register(
            "policy_engine",
            lambda: self.kernel.policy_engine
        )

        self.kernel.bootstrap_graph.register(
            "agent_runtime",
            lambda: self.kernel.agent_runtime
        )

        self.kernel.bootstrap_graph.register(
            "memory_intelligence",
            lambda: self.kernel.memory_intelligence
        )

        self.kernel.bootstrap_graph.register(
            "supervisor",
            lambda: self.kernel.supervisor
        )

    def execute(self):
        return self.kernel.bootstrap_graph.execute()
