from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ExecutiveContext:

    goal_id: str

    objective: str

    permissions: Dict = field(
        default_factory=dict
    )

    selected_skills: List[str] = field(
        default_factory=list
    )

    execution_plan: List[Dict] = field(
        default_factory=list
    )

    results: List[Dict] = field(
        default_factory=list
    )


    def add_result(
        self,
        result: Dict,
    ):

        self.results.append(
            result
        )
