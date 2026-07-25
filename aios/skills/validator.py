class SkillValidator:


    REQUIRED_FIELDS = [
        "name",
        "description",
        "capability",
    ]


    def validate(
        self,
        skill,
    ):

        errors = []


        for field in self.REQUIRED_FIELDS:

            if not skill.get(field):

                errors.append(
                    f"Missing field: {field}"
                )


        return {
            "valid":
                len(errors) == 0,

            "errors":
                errors,
        }
