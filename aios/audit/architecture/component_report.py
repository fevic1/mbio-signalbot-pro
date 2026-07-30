from dataclasses import dataclass


@dataclass
class ComponentOwnership:

    name: str
    implementations: list
    canonical: str | None = None
    status: str = "untracked"
    risk: str = "unknown"
    owner: str | None = None


    def to_dict(self):

        return {
            "name": self.name,
            "implementations": self.implementations,
            "canonical": self.canonical,
            "status": self.status,
            "risk": self.risk,
            "owner": self.owner,
        }
