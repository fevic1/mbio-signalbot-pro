from .gate_registry import GateRegistry

from aios.governance.gates import (
    EvidenceGate,
    SecurityGate,
    DependencyGate,
    RegressionGate,
)


class CouncilGovernance:


    def __init__(self):

        self.registry = GateRegistry()

        self.registry.register(
            EvidenceGate()
        )

        self.registry.register(
            SecurityGate()
        )

        self.registry.register(
            DependencyGate()
        )

        self.registry.register(
            RegressionGate()
        )



    def validate(
        self,
        context,
    ):

        return self.registry.run(
            context
        )
