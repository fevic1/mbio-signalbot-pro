from dataclasses import dataclass, field


@dataclass
class ProjectDecision:

    action: str

    reason: str

    priority: str = "normal"

    metadata: dict = field(
        default_factory=dict
    )


    def describe(self):

        return {
            "action": self.action,
            "reason": self.reason,
            "priority": self.priority,
            "metadata": self.metadata,
        }
