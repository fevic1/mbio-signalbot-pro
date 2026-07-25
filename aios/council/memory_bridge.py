from .decision_context import DecisionContext
from .retrieval import CouncilRetrieval


class CouncilMemoryBridge:


    def __init__(
        self,
        council_memory,
    ):

        self.memory = council_memory

        self.retrieval = CouncilRetrieval(
            council_memory
        )



    def get_context(
        self,
        question,
    ):

        decisions = (
            self.retrieval.retrieve(
                question
            )
        )


        context = DecisionContext(
            decisions
        )


        return context.build()



    def remember(
        self,
        session,
    ):

        return self.memory.store(
            session
        )
