from aios.policy import (
    PolicyEngine as CanonicalPolicyEngine,
    Policy,
)


class PolicyEngineAdapter:

    def __init__(self):
        self.engine = CanonicalPolicyEngine()

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
