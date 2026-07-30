from .ownership import OwnershipRegistry
from .component_report import ComponentOwnership


class OwnershipAnalyzer:


    def __init__(
        self,
        registry=None,
    ):
        self.registry = registry or OwnershipRegistry()


    def analyze(
        self,
        duplicates,
    ):

        results = []

        for name, locations in duplicates.items():

            record = self.registry.get(name)

            results.append(
                ComponentOwnership(
                    name=name,
                    implementations=locations,
                    canonical=record.get(
                        "canonical"
                    ),
                    status=record.get(
                        "status",
                        "untracked",
                    ),
                    risk=record.get(
                        "risk",
                        "unknown",
                    ),
                    owner=record.get(
                        "owner"
                    ),
                )
            )

        return results
