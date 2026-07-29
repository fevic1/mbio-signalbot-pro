from dataclasses import dataclass


@dataclass
class RuntimeConfig:

    interval_seconds: int = 60

    enabled: bool = True
