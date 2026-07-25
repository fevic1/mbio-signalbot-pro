
class CouncilExecutor:


    ROLE_PIPELINES = {

        "architect": "engineering",

        "quant": "trading",

        "risk": "trading",

        "research": "research",

        "verification": "research",

        "skeptic": "research",

    }


    def __init__(
        self,
        execution_executor,
    ):

        self.execution_executor = execution_executor



    async def execute(
        self,
        agent,
        question,
    ):

        category = self.ROLE_PIPELINES.get(
            agent.name,
            "research",
        )


        task = {

            "category": category,

            "objective": question,

            "agent": agent.name,

        }


        context = await self.execution_executor.execute(
            task
        )


        return {

            "agent": agent.name,

            "category": category,

            "results": context.results,

            "status": context.status,

        }
