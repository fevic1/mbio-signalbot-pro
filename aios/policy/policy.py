from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass(slots=True)
class Policy:
    name: str
    evaluator: Callable[..., bool]
    metadata: dict = field(default_factory=dict)

    def evaluate(self, *args, **kwargs) -> bool:
        return bool(self.evaluator(*args, **kwargs))
