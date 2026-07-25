class GovernanceRule:


    def __init__(
        self,
        name,
        description,
        check,
    ):

        self.name = name
        self.description = description
        self._check = check



    def check(
        self,
        context,
    ):

        return self._check(
            context
        )



def required_field(
    field,
):

    def check(
        context,
    ):

        passed = (
            field in context
            and context[field] is not None
        )

        return {
            "rule": field,
            "passed": passed,
            "message":
                (
                    "ok"
                    if passed
                    else f"Missing {field}"
                ),
        }

    return GovernanceRule(
        name=f"required_{field}",
        description=f"Requires {field}",
        check=check,
    )
