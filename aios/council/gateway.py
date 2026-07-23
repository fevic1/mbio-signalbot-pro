from .council import Council


class CouncilGateway:

    def __init__(self, council=None):

        self.council = council or Council()


    async def review(
        self,
        execution,
    ):

        decision = await self.council.evaluate(
            execution
        )

        if not decision.approved:
            raise RuntimeError(
                decision.reason
            )

        return decision
