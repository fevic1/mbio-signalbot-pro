from .engine import ExecutionEngine


class ExecutionRunner(ExecutionEngine):

    def execute(self, context=None):
        return self.run(context)
