class RuntimeIdentityStore:

    def __init__(self):
        self._identities = {}

    def register(self, name: str, identity):
        self._identities[name] = identity
        return identity

    def unregister(self, name: str):
        return self._identities.pop(name, None)

    def get(self, name: str, default=None):
        return self._identities.get(name, default)

    def names(self):
        return tuple(sorted(self._identities))

    def export(self):
        return {
            name: type(identity).__name__
            for name, identity in self._identities.items()
        }

    def clear(self):
        self._identities.clear()

    def __contains__(self, name):
        return name in self._identities

    def __len__(self):
        return len(self._identities)
