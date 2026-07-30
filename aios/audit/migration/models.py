from dataclasses import dataclass, field


@dataclass
class MigrationManifest:

    component: str
    canonical: str
    owner: str
    risk: str

    implementations: list[str] = field(
        default_factory=list
    )

    affected_imports: list[str] = field(
        default_factory=list
    )

    rollback_plan: str = (
        "Restore previous import routing"
    )

    status: str = (
        "migration_pending"
    )


    def to_dict(self):

        return {
            "component": self.component,
            "canonical": self.canonical,
            "owner": self.owner,
            "risk": self.risk,
            "implementations": self.implementations,
            "affected_imports": self.affected_imports,
            "rollback_plan": self.rollback_plan,
            "status": self.status,
        }
