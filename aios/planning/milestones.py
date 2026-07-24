from typing import List, Dict


class MilestoneGenerator:


    def generate(
        self,
        plan,
    ) -> List[Dict]:

        strategy = (
            plan.strategy.lower()
        )

        milestones = []


        if "research" in strategy:

            milestones.append(
                {
                    "name": "Research",
                    "description": (
                        "Collect and validate required knowledge"
                    ),
                    "status": "pending",
                }
            )


        if "design" in strategy:

            milestones.append(
                {
                    "name": "Architecture",
                    "description": (
                        "Design system structure and approach"
                    ),
                    "status": "pending",
                }
            )


        if "implement" in strategy:

            milestones.append(
                {
                    "name": "Development",
                    "description": (
                        "Build required components"
                    ),
                    "status": "pending",
                }
            )


        if "validate" in strategy:

            milestones.append(
                {
                    "name": "Testing",
                    "description": (
                        "Verify correctness and quality"
                    ),
                    "status": "pending",
                }
            )


        if "deploy" in strategy:

            milestones.append(
                {
                    "name": "Deployment",
                    "description": (
                        "Release operational system"
                    ),
                    "status": "pending",
                }
            )


        if "improve" in strategy:

            milestones.append(
                {
                    "name": "Improvement",
                    "description": (
                        "Measure results and optimize"
                    ),
                    "status": "pending",
                }
            )


        plan.milestones = milestones

        return milestones
