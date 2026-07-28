from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class Tool:
    name: str
    handler: Callable[..., Any]
    description: str = ""
    metadata: dict = field(default_factory=dict)

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)
