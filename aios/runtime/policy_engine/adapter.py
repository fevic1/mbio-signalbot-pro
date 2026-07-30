from aios.policy import (
    PolicyEngine as CanonicalPolicyEngine,
    Policy,
)

from aios.runtime.governance_loader import GovernanceLoader


class PolicyEngineAdapter:

    def __init__(self):
        self.engine = CanonicalPolicyEngine()

        self.governance = GovernanceLoader().load()

        self._register_governance_rules()


    def _register_governance_rules(self):

        self.register(
            "governance_loaded",
            lambda context: (
                self.governance.metadata.get(
                    "governance_loaded",
                    False
                )
            ),
        )

        self.register(
            "safe_mode_enabled",
            lambda context: True,
        )

        self.register(
            "telemetry_required",
            lambda context: (
                context.get(
                    "telemetry_active",
                    False
                )
                if isinstance(context, dict)
                else False
            ),
        )


    def register(self, name, rule):

        policy = Policy(
            name=name,
            evaluator=rule,
        )

        return self.engine.register(policy)


    def evaluate(self, context):

        results = {}

        for policy in self.engine._policies.values():

            results[policy.name] = bool(
                policy.evaluate(context)
            )

        return {
            "allowed": all(results.values()),
            "checks": results,
        }


    def remove(self, name):

        return self.engine.unregister(name)


    def list(self):

        return tuple(
            self.engine._policies.keys()
        )
