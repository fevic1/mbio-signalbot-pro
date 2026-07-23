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

    def __init__(self):
        self.executor = CapabilityExecutor()

    def execute(self, context):
        result = self.run(context)
        context.set_metadata("council", result)
        return result

    def run(self, context):
        opinions = {}

        for advisor in self.ADVISORS:
            opinions[advisor] = self.executor.execute(
                CapabilityRequest(
                    capability=advisor,
                    context=context.metadata,
                )
            )

        return {
            "skill": self.id,
            "opinions": opinions,
        }
