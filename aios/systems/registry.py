from typing import Dict, List

from aios.core.registry import Registry
from .models import ManagedSystem


class SystemRegistry(Registry[ManagedSystem]):

    def register(self, system: ManagedSystem):
        return super().register(system.name, system)

    def remove(self, name: str):
        return self.unregister(name)

    def list_systems(self) -> List[Dict]:
        return [
            system.describe()
            for system in self.all()
        ]

    def find_capability(self, capability: str):
        return [
            system
            for system in self.all()
            if system.has_capability(capability)
        ]
