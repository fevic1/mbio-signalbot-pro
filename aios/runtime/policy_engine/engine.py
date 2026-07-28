
class PolicyEngine:

    def __init__(self):
        self.rules = {}

    def register(self, name, rule):
        self.rules[name] = rule

    def evaluate(self, context):
        results = {}

        for name, rule in self.rules.items():
            results[name] = bool(
                rule(context)
            )

        return {
            "allowed": all(results.values()),
            "checks": results,
        }

    def remove(self, name):
        return self.rules.pop(
            name,
            None
        )

    def list(self):
        return tuple(self.rules)
