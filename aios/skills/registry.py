from aios.core.registry import Registry


class SkillRegistry(Registry):

    def register(self, skill):
        return super().register(skill.id, skill)

    def all(self):
        return list(super().all())
