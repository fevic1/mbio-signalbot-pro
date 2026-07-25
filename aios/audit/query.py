class AuditQuery:


    def __init__(
        self,
        storage,
    ):

        self.storage = storage



    def all_decisions(
        self,
    ):

        return self.storage.read(
            "decisions"
        )



    def failed_decisions(
        self,
    ):

        decisions = self.all_decisions()

        return [

            item

            for item in decisions

            if not item["decision"].get(
                "approved",
                False
            )

        ]



    def find_by_gate(
        self,
        gate,
    ):

        governance = self.storage.read(
            "governance"
        )


        results = []


        for item in governance:

            for result in item.get(
                "results",
                []
            ):

                if result.get(
                    "gate"
                ) == gate:

                    results.append(
                        item
                    )


        return results



    def search_question(
        self,
        keyword,
    ):

        sessions = self.storage.read(
            "sessions"
        )


        keyword = keyword.lower()


        return [

            session

            for session in sessions

            if keyword in session.get(
                "question",
                ""
            ).lower()

        ]
