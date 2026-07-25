class CouncilReportBuilder:


    def build(
        self,
        session,
    ):

        return {

            "question":
                session.question,

            "participants":
                session.participants,

            "assignments":
                [
                    a.describe()
                    if hasattr(a, "describe")
                    else a
                    for a in session.assignments
                ],

            "messages":
                [
                    m.describe()
                    if hasattr(m, "describe")
                    else m
                    for m in session.messages
                ],

            "artifacts":
                (
                    [
                        a.describe()
                        if hasattr(a, "describe")
                        else a
                        for a in session.artifacts
                    ]
                    +
                    [
                        response["artifact"]
                        for item in session.responses
                        if isinstance(item.get("response"), dict)
                        and "artifact" in item["response"]
                        for response in [
                            item["response"]
                        ]
                    ]
                ),

            "responses":
                session.responses,

        }
