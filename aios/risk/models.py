from dataclasses import dataclass, field


@dataclass
class RiskDecision:

    allowed: bool

    reason: str

    limits: dict = field(
        default_factory=dict
    )

    def describe(self):
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "limits": self.limits,
        }
