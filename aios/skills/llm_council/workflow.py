from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest
from aios.skills.base import Skill


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    ADVISORS = [
        "research",
        "reasoning",
        "verification",
    ]

    CHAIRMAN = "reasoning"

    def __init__(self):
        self.executor = CapabilityExecutor()

    def execute(self, context):
        result = self.run(context)
        context.set_metadata("council", result)
        return result

    def _call(self, capability, context):
        return self.executor.execute(
            CapabilityRequest(
                capability=capability,
                context=context,
            )
        )

    def run(self, context):

        opinions = {}

        for advisor in self.ADVISORS:
            opinions[advisor] = self._call(
                advisor,
                context.metadata,
            )

        reviews = {}

        for reviewer in self.ADVISORS:

            reviews[reviewer] = self._call(
                reviewer,
                {
                    "role": "peer_review",
                    "opinions": opinions,
                },
            )

        chairman = self._call(
            self.CHAIRMAN,
            {
                "role": "chairman",
                "opinions": opinions,
                "reviews": reviews,
            },
        )

        return {
            "skill": self.id,
            "opinions": opinions,
            "reviews": reviews,
            "decision": chairman,
        }
