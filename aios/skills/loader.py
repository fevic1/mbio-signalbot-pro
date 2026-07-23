from .registry import SkillRegistry


class SkillLoader:

    def __init__(self):
        self.registry = SkillRegistry()

    def load(self):
        from .llm_council.workflow import LLMCouncilSkill

        self.registry.register(
            LLMCouncilSkill()
        )

        return self.registry
