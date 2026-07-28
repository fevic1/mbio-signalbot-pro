class RuntimeValidator:

    def __init__(self):
        self._rules = {}

    def register(self, name: str, validator):
        self._rules[name] = validator
        return validator

    def remove(self, name: str):
        return self._rules.pop(name, None)

    def validate(self, name: str, value):
        rule = self._rules[name]
        return bool(rule(value))

    def validate_all(self, value):
        results = {}

        for name, rule in self._rules.items():
            results[name] = bool(rule(value))

        return results

    def rules(self):
        return tuple(sorted(self._rules))

    def clear(self):
        self._rules.clear()

    def __contains__(self, name):
        return name in self._rules

    def __len__(self):
        return len(self._rules)
