class SkillRegistry:

    def __init__(self):
        self._skills = {}

    def register(self, skill):
        self._skills[skill.id] = skill

    def get(self, skill_id):
        return self._skills.get(skill_id)

    def all(self):
        return list(self._skills.values())

