from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Plan:

    objective: str

    strategy: str = ""

    milestones: List[Dict] = field(
        default_factory=list
    )

    required_capabilities: List[str] = field(
        default_factory=list
    )

    success_criteria: List[str] = field(
        default_factory=list
    )


    def add_milestone(
        self,
        milestone,
    ):

        self.milestones.append(
            milestone
        )


    def add_capability(
        self,
        capability,
    ):

        if capability not in self.required_capabilities:

            self.required_capabilities.append(
                capability
            )


    def add_criteria(
        self,
        criteria,
    ):

        self.success_criteria.append(
            criteria
        )


    def describe(self):

        return {
            "objective": self.objective,
            "strategy": self.strategy,
            "milestones": self.milestones,
            "required_capabilities": self.required_capabilities,
            "success_criteria": self.success_criteria,
        }
