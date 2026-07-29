from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillManifest:

    name: str

    description: str

    permission: str

    handler: Any = None

    input_schema: dict = field(
        default_factory=dict
    )

    memory_enabled: bool = True

    llm_instructions: str = ""

    timeout: int = 60

    retry_limit: int = 2


    def validate(self):

        if not self.name:
            raise ValueError(
                "Skill name required"
            )

        if not self.permission:
            raise ValueError(
                "Skill permission required"
            )

        return True
