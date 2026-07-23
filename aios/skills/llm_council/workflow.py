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

        manifest = Path(__file__).parent / "manifest.yaml"
        self.config = yaml.safe_load(manifest.read_text())

    def execute(self, context):
        result = asyncio.run(self.run(context))
        context.set_metadata("council", result)
        return result

    async def invoke(self, capability, payload):
        return await asyncio.to_thread(
            self.executor.execute,
            CapabilityRequest(
                capability=capability,
                context=payload,
            ),
        )

    async def run(self, context):

        advisors = self.config["advisors"]

        opinion_results = await asyncio.gather(
            *[
                self.invoke(
                    advisor,
                    context.metadata,
                )
                for advisor in advisors
            ]
        )

        opinions = dict(zip(advisors, opinion_results))

        review_results = await asyncio.gather(
            *[
                self.invoke(
                    reviewer,
                    {
                        "stage": "peer_review",
                        "opinions": opinions,
                    },
                )
                for reviewer in advisors
            ]
        )

        reviews = dict(zip(advisors, review_results))

        decision = await self.invoke(
            self.config["chairman"],
            {
                "stage": "synthesis",
                "opinions": opinions,
                "reviews": reviews,
            },
        )

        return {
            "manifest": self.config["id"],
            "opinions": opinions,
            "reviews": reviews,
            "decision": decision,
        }
