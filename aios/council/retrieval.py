class CouncilRetrieval:


    def __init__(
        self,
        memory,
    ):

        self.memory = memory



    def retrieve(
        self,
        question,
        limit=5,
    ):

        results = (
            self.memory.find(
                question
            )
        )

        return results[:limit]
