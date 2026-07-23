import asyncio
from pathlib import Path

import yaml

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest
from aios.skills.base import Skill


class LLMCouncilSkill(Skill):

    id = "llm-council"
    name = "LLM Council"

    def __init__(self):
        self.executor = CapabilityExecutor()
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

            return dict(zip(advisors, results))

        actor = stage["actor"]

        return await self.invoke(
            actor,
            state,
        )

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
