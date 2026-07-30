from dataclasses import dataclass, field


@dataclass
class MigrationReport:

    component: str

    canonical: str

    dependencies: list = field(
        default_factory=list
    )

    adapter_required: bool = False


    def to_dict(self):

        return {
            "component": self.component,
            "canonical": self.canonical,
            "dependencies": self.dependencies,
            "adapter_required": self.adapter_required,
        }
