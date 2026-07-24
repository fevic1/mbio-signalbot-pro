from typing import Dict, List

from .models import ManagedSystem


class SystemRegistry:

    def __init__(self):

        self.systems: Dict[str, ManagedSystem] = {}


    def register(
        self,
        system: ManagedSystem,
    ):

        self.systems[
            system.name
        ] = system

        return system


    def get(
        self,
        name: str,
    ):

        return self.systems.get(
            name
        )


    def remove(
        self,
        name: str,
    ):

        return self.systems.pop(
            name,
            None,
        )


    def list_systems(
        self,
    ) -> List[Dict]:

        return [
            system.describe()
            for system in self.systems.values()
        ]


    def find_capability(
        self,
        capability: str,
    ):

        return [
            system
            for system in self.systems.values()
            if system.has_capability(capability)
        ]
