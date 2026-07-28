class RuntimePolicyRegistry:

    def __init__(self):
        self._policies: dict[str, object] = {}

    def register(self, name: str, policy):
        self._policies[name] = policy

    def unregister(self, name: str):
        self._policies.pop(name, None)

    def get(self, name: str, default=None):
        return self._policies.get(name, default)

    def names(self):
        return tuple(sorted(self._policies))

    def export(self):
        return {
            name: type(policy).__name__
            for name, policy in self._policies.items()
        }

    def __contains__(self, name):
        return name in self._policies

    def __len__(self):
        return len(self._policies)
