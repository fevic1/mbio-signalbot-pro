from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionContext:
    execution_label: str
    strategy: str
    regime: str
    order_type: str
