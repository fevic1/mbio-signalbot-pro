class CouncilMemory:

    def __init__(self):

        self.history = []

    def store(self, report):

        self.history.append(report)

    def recent(self, limit=20):

        return self.history[-limit:]
