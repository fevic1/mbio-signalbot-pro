class RuntimeSecretManager:

    def __init__(self):
        self._secrets = {}

    def set(self, name: str, value: str):
        self._secrets[name] = value
        return name

    def get(self, name: str, default=None):
        return self._secrets.get(name, default)

    def remove(self, name: str):
        return self._secrets.pop(name, None)

    def exists(self, name: str):
        return name in self._secrets

    def names(self):
        return tuple(sorted(self._secrets))

    def export(self):
        return {
            name: "***"
            for name in self._secrets
        }

    def clear(self):
        self._secrets.clear()

    def __contains__(self, name):
        return name in self._secrets

    def __len__(self):
        return len(self._secrets)
