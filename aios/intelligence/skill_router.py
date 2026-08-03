class SkillRouter:

    def route(
        self,
        request,
        skills,
    ):

        request = request.lower()

        selected = []

        for item in skills:

            key = (
                item["server"]
                + " "
                + item["tool"]
            ).lower()

            if any(
                token in key
                for token in request.split()
            ):
                selected.append(item)

        return selected or skills[:5]
