from pathlib import Path

import yaml

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest
from aios.skills.base import Skill


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    def __init__(self):
        self.executor = CapabilityExecutor()

        manifest = (
            Path(__file__).parent / "manifest.yaml"
        )

        self.config = yaml.safe_load(
            manifest.read_text()
        )

    def execute(self, context):
        result = self.run(context)
        context.set_metadata("council", result)
        return result

    def call(self, capability, payload):
        return self.executor.execute(
            CapabilityRequest(
                capability=capability,
                context=payload,
            )
        )

    def run(self, context):

        opinions = {}

        for advisor in self.config["advisors"]:
            opinions[advisor] = self.call(
                advisor,
                context.metadata,
            )

        reviews = {}

        for reviewer in self.config["advisors"]:
            reviews[reviewer] = self.call(
                reviewer,
                {
                    "stage": "peer_review",
                    "opinions": opinions,
                },
            )

        decision = self.call(
            self.config["chairman"],
            {
                "stage": "synthesis",
                "opinions": opinions,
                "reviews": reviews,
            },
        )

        return {
            "manifest": self.config["id"],
            "opinions": opinions,
            "reviews": reviews,
            "decision": decision,
        }
