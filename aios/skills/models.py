from dataclasses import dataclass, field


@dataclass
class SkillDefinition:

    name: str

    description: str

    capabilities: list[str] = field(
        default_factory=list
    )

    triggers: list[str] = field(
        default_factory=list
    )

    quality_gates: list[str] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )


    def supports(
        self,
        request,
    ):

        capability = request.get(
            "capability"
        )

        trigger = request.get(
            "trigger"
        )


        if capability:
            return (
                capability
                in self.capabilities
            )


        if trigger:
            return (
                trigger
                in self.triggers
            )


        return False


    def describe(self):

        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "triggers": self.triggers,
            "quality_gates": self.quality_gates,
        }
