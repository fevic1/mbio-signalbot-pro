class SkillRegistryAdapter:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def register(
        self,
        skill,
    ):

        return self.registry.register(
            skill
        )



    def list_skills(
        self,
    ):

        return list(
            self.registry.skills.values()
        )



    def find(
        self,
        request,
    ):

        matches = []

        for skill in self.list_skills():

            if skill.supports(
                request
            ):

                matches.append(
                    skill
                )


        return matches
