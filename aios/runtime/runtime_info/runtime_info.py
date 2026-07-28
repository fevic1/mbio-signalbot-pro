from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeInfo:
    name: str = "AIOS Runtime"
    description: str = "Institutional AI Operating System"
    vendor: str = "AIOS"
    homepage: str = ""
    license: str = ""
    metadata: dict = field(default_factory=dict)

    def export(self):
        return {
            "name": self.name,
            "description": self.description,
            "vendor": self.vendor,
            "homepage": self.homepage,
            "license": self.license,
            "metadata": dict(self.metadata),
        }
