class CouncilMemory:


    def __init__(self):

        self.records = []



    def store(
        self,
        session,
    ):

        record = session.describe()

        self.records.append(
            record
        )

        return record



    def history(
        self,
    ):

        return self.records



    def find(
        self,
        keyword,
    ):

        keyword = keyword.lower()

        return [
            item
            for item in self.records
            if keyword in item["question"].lower()
        ]
