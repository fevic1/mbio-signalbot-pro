from datetime import datetime, timezone


class MemoryActivationScore:


    def calculate(
        self,
        memory,
    ):

        importance = {
            "critical": 100,
            "high": 75,
            "normal": 50,
            "low": 25,
        }


        score = importance.get(
            memory.importance.value,
            0,
        )


        score += (
            memory.metadata.confidence
            * 20
        )


        score += (
            memory.metadata.access_count
            * 3
        )


        return score
