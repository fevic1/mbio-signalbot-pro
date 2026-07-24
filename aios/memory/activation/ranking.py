from .scoring import MemoryActivationScore


class MemoryRanker:


    def __init__(self):

        self.scorer = MemoryActivationScore()



    def rank(
        self,
        memories,
    ):

        return sorted(
            memories,
            key=self.scorer.calculate,
            reverse=True,
        )
