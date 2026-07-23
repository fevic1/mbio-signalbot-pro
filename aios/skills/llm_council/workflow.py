from aios.skills.base import Skill


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    def execute(self, context):
        context.set_metadata(
            "skill",
            self.id,
        )

        event_bus = getattr(context, "event_bus", None)

        if event_bus:
            event_bus.publish(
                "skill.started",
                {
                    "skill": self.id,
                },
            )

        result = self.run(context)

        context.set_metadata(
            "skill_result",
            result,
        )

        if event_bus:
            event_bus.publish(
                "skill.completed",
                {
                    "skill": self.id,
                },
            )

        return result

    def run(self, context):
        raise NotImplementedError(
            "LLM Council execution not implemented."
        )
