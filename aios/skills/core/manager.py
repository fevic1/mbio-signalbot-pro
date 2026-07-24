from .registry import SkillRegistry


class SkillManager:


    def __init__(
        self,
        registry=None,
    ):

        self.registry = (
            registry
            or SkillRegistry()
        )


    def install(
        self,
        skill,
    ):

        self.registry.register(
            skill
        )

        skill.activate()

        return skill


    def remove(
        self,
        name,
    ):

        skill = self.registry.get(
            name
        )

        if skill:

            skill.deactivate()

        return skill


    def available(
        self,
    ):

        return [
            skill
            for skill in self.registry.skills.values()
            if skill.status == "active"
        ]


    def capabilities(
        self,
    ):

        result = {}

        for skill in self.available():

            result[
                skill.name
            ] = skill.capabilities

        return result
