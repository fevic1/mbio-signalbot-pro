from aios.core.identifiable import Identifiable

from .scoring import MemoryActivationScore


class MemoryRanker(Identifiable):


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
