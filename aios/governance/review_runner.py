from aios.council.agent_executor import CouncilAgentExecutor


class CouncilReviewRunner:


    def __init__(
        self,
        council,
        consensus,
    ):

        self.council = council

        self.consensus = consensus

        self.agent_executor = CouncilAgentExecutor(
            council.agent_manager
        )



    async def review(
        self,
        issue,
    ):

        session = (
            self.council.create_session(
                issue.title
            )
        )


        agents = [
            "architect",
            "risk",
            "skeptic",
            "verification",
        ]


        self.council.assign_agents(
            session,
            agents,
        )


        # Placeholder responses.
        # Real agent runtime will populate these.
        for agent in agents:

            response = await self.agent_executor.review(
                agent,
                issue,
            )

            self.council.add_response(
                session,
                agent,
                response,
            )


        decision = (
            self.council.finalize(
                session,
                self.consensus,
            )
        )


        issue.status = (
            "resolved"
            if decision["approved"]
            else "rejected"
        )


        return {
            "issue": issue.describe(),
            "decision": decision,
            "session": session.describe(),
        }



    def generate_review(
        self,
        agent,
        issue,
    ):

        return (
            f"{agent} reviewed "
            f"{issue.title}"
        )
