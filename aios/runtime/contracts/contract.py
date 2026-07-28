from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeContract:
    name: str
    version: str = "1.0.0"
    requirements: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class RuntimeContractRegistry:

    def __init__(self):
        self._contracts = {}

    def register(self, contract: RuntimeContract):
        self._contracts[contract.name] = contract
        return contract

    def unregister(self, name: str):
        return self._contracts.pop(name, None)

    def get(self, name: str):
        return self._contracts.get(name)

    def validate(self, name: str, available):
        contract = self._contracts[name]

        return all(
            requirement in available
            for requirement in contract.requirements
        )

    def all(self):
        return tuple(self._contracts.values())

    def export(self):
        return {
            name: {
                "version": contract.version,
                "requirements": contract.requirements,
            }
            for name, contract in self._contracts.items()
        }

    def clear(self):
        self._contracts.clear()

    def __contains__(self, name):
        return name in self._contracts

    def __len__(self):
        return len(self._contracts)
