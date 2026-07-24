from typing import Dict, List

from .models import Skill


class SkillRegistry:


    def __init__(self):

        self.skills: Dict[str, Skill] = {}


    def register(
        self,
        skill: Skill,
    ):

        self.skills[
            skill.name
        ] = skill

        return skill


    def get(
        self,
        name: str,
    ):

        return self.skills.get(
            name
        )


    def remove(
        self,
        name: str,
    ):

        return self.skills.pop(
            name,
            None,
        )


    def list_skills(
        self,
    ) -> List[Dict]:

        return [
            skill.describe()
            for skill in self.skills.values()
        ]


    def find_capability(
        self,
        capability: str,
    ):

        return [
            skill
            for skill in self.skills.values()
            if skill.supports(capability)
        ]
