from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeManifest:
    name: str
    version: str = "1.0.0"
    services: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
