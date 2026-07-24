from ..models import MemoryImportance


class MemoryPriority:


    def score(
        self,
        memory,
    ):

        score = 0


        importance_scores = {
            MemoryImportance.CRITICAL: 100,
            MemoryImportance.HIGH: 75,
            MemoryImportance.NORMAL: 50,
            MemoryImportance.LOW: 25,
        }


        score += importance_scores.get(
            memory.importance,
            0,
        )


        score += (
            memory.metadata.confidence
            * 20
        )


        score += (
            memory.metadata.access_count
            * 2
        )


        return score



    def rank(
        self,
        memories,
    ):

        return sorted(
            memories,
            key=self.score,
            reverse=True,
        )
