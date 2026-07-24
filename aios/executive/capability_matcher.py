from typing import List


class CapabilityMatcher:


    def __init__(
        self,
        skill_manager,
    ):

        self.skill_manager = skill_manager


    def required_capabilities(
        self,
        goal,
    ) -> List[str]:

        text = (
            goal.objective
            .lower()
        )

        capabilities = []


        rules = {
            "code": [
                "code",
                "develop",
                "implement",
                "fix",
            ],

            "review": [
                "review",
                "audit",
                "inspect",
            ],

            "verification": [
                "verify",
                "validate",
                "test",
            ],

            "analysis": [
                "analyze",
                "analysis",
                "research",
            ],

            "planning": [
                "plan",
                "strategy",
                "design",
            ],
        }


        for capability, keywords in rules.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                capabilities.append(
                    capability
                )


        if not capabilities:

            capabilities.append(
                "reasoning"
            )


        return capabilities



    def match(
        self,
        goal,
    ):

        required = self.required_capabilities(
            goal
        )

        matched = []


        for skill in self.skill_manager.available():

            score = len(
                set(required)
                &
                set(skill.capabilities)
            )


            if score > 0:

                matched.append(
                    {
                        "skill": skill.name,
                        "capabilities": skill.capabilities,
                        "match_score": score,
                    }
                )


        return {
            "required_capabilities": required,
            "matched_skills": matched,
        }
