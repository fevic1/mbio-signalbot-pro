from dataclasses import dataclass


@dataclass(slots=True)
class Credential:
    name: str
    provider: str
    value: str
    metadata: dict


class RuntimeCredentialManager:

    def __init__(self):
        self._credentials: dict[str, Credential] = {}

    def register(
        self,
        name: str,
        provider: str,
        value: str,
        metadata=None,
    ):
        credential = Credential(
            name=name,
            provider=provider,
            value=value,
            metadata=metadata or {},
        )

        self._credentials[name] = credential
        return credential

    def get(self, name: str):
        return self._credentials.get(name)

    def remove(self, name: str):
        return self._credentials.pop(name, None)

    def exists(self, name: str):
        return name in self._credentials

    def names(self):
        return tuple(sorted(self._credentials))

    def export(self):
        return {
            name: {
                "provider": credential.provider,
                "metadata": credential.metadata,
            }
            for name, credential in self._credentials.items()
        }

    def clear(self):
        self._credentials.clear()

    def __contains__(self, name):
        return name in self._credentials

    def __len__(self):
        return len(self._credentials)
