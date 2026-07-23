from aios.skills.base import Skill


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    def execute(self, context):
        raise NotImplementedError(
            "LLM Council workflow not implemented."
        )
