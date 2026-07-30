from .policy import Policy
from .result import PolicyResult


class PolicyEngine:

    def __init__(self):
        self._policies: dict[str, Policy] = {}

    def register(self, policy: Policy):
        self._policies[policy.name] = policy
        return policy

    def unregister(self, name: str):
        return self._policies.pop(name, None)

    def get(self, name: str):
        return self._policies[name]

    def evaluate(self, name: str, *args, **kwargs):
        policy = self.get(name)
        allowed = policy.evaluate(*args, **kwargs)
        return PolicyResult(
            allowed=allowed,
            policy=policy.name,
            severity=policy.severity,
            reason="" if allowed else "Policy denied",
        )

    def evaluate_all(self, *args, **kwargs):
        results = []
        for policy in self._policies.values():
            results.append(
                PolicyResult(
                    allowed=policy.evaluate(*args, **kwargs),
                    policy=policy.name,
                    severity=policy.severity,
                )
            )
        return results

    def __contains__(self, name):
        return name in self._policies

    def __len__(self):
        return len(self._policies)
