from aios.core.execution.runner import ExecutionRunner

class PolicyEngine(ExecutionRunner):

    def review(self, proposal):

        return {
            "allowed": True,
            "violations": [],
        }
