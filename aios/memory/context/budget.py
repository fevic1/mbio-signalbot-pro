class ContextBudget:


    def __init__(
        self,
        max_items=20,
    ):

        self.max_items = max_items



    def apply(
        self,
        memories,
    ):

        return memories[
            :self.max_items
        ]
