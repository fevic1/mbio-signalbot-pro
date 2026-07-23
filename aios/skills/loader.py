from importlib import import_module

from .core.manager import SkillManager
from .registry import SkillRegistry


class SkillLoader:

    def __init__(
        self,
        system=None,
    ):
        self.system = system
        self.registry = SkillRegistry()
        self.manager = SkillManager("aios/skills")

    def load(self):

        for manifest in self.manager.enabled():

            module = import_module(
                f'aios.skills.{manifest["id"].replace("-", "_")}.workflow'
            )

            skill = getattr(module, "LLMCouncilSkill")(
                self.system
            )

            self.registry.register(skill)

        return self.registry
