import asyncio
from pathlib import Path

import yaml

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest
from aios.skills.base import Skill
from aios.events import Event


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    def __init__(
        self,
        system=None,
    ):
        self.system = system
        self.executor = CapabilityExecutor(
            system
        )
        self.config = yaml.safe_load(
            (Path(__file__).parent / "manifest.yaml").read_text()
        )

    async def execute(self, context):
        result = await self.run(context)
        context.set_metadata("council", result)
        return result

    async def invoke(self, capability, payload):
        return await self.executor.execute(
            CapabilityRequest(
                capability=capability,
                context=payload,
            ),
        )

    async def execute_stage(self, stage, state):

        if self.system and self.system.event_bus:
            self.system.event_bus.publish(
                Event(
                    "council_stage_started",
                    source="llm-council",
                    payload={
                        "stage": stage["stage"],
                    },
                )
            )

        advisors = self.config["advisors"]

        if stage["parallel"]:

            results = await asyncio.gather(
                *[
                    self.invoke(
                        advisor,
                        state,
                    )
                    for advisor in advisors
                ]
            )

            output = dict(zip(advisors, results))

            if self.system and self.system.event_bus:
                self.system.event_bus.publish(
                    Event(
                        "council_stage_completed",
                        source="llm-council",
                        payload={
                            "stage": stage["stage"],
                            "advisors": advisors,
                        },
                    )
                )

            return output

        actor = stage["actor"]

        result = await self.invoke(
            actor,
            state,
        )

        if self.system and self.system.event_bus:
            self.system.event_bus.publish(
                Event(
                    "council_stage_completed",
                    source="llm-council",
                    payload={
                        "stage": stage["stage"],
                        "actor": actor,
                    },
                )
            )

        return result

    async def run(self, context):

        state = {
            "context": context.metadata,
        }

        history = {}

        for stage in self.config["workflow"]:

            state.update(history)

            history[stage["stage"]] = await self.execute_stage(
                stage,
                state,
            )

        return history
