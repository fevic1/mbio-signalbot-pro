from aios.core.identifiable import Identifiable

class MemoryContext(Identifiable):


    def __init__(
        self,
        retriever,
    ):

        self.retriever = retriever


    def build(
        self,
        question,
    ):

        return {

            "question":
                question,

            "previous_decisions":
                self.retriever.by_category(
                    "decision"
                ),

            "policies":
                self.retriever.by_category(
                    "policy"
                ),

            "failures":
                self.retriever.by_category(
                    "failure"
                ),
        }
