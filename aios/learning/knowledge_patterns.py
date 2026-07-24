class KnowledgePatternStore:


    def __init__(self):

        self.patterns = []



    def add(
        self,
        lesson,
    ):

        self.patterns.append(
            lesson
        )

        return lesson



    def search(
        self,
        category=None,
    ):

        if not category:

            return self.patterns


        return [
            pattern
            for pattern in self.patterns
            if pattern.get(
                "type"
            ) == category
        ]
