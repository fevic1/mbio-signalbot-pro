
from datetime import datetime, timezone


class WorkflowEngine:

    def __init__(self):
        self.workflows = {}

    def register(self, name, steps):
        self.workflows[name] = steps

    def execute(self, name, context=None):
        context = context or {}

        for step in self.workflows[name]:
            context = step(context)

        return {
            "workflow": name,
            "result": context,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def list(self):
        return tuple(self.workflows)
