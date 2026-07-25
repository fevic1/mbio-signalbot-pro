class EvidenceBuilder:


    def build(
        self,
        feedback_records,
    ):

        evidence = []


        for record in feedback_records:

            content = record.content


            evidence.append(
                {

                    "change_id":
                        content.get(
                            "change_id"
                        ),

                    "improved":
                        content.get(
                            "evaluation",
                            {}
                        ).get(
                            "improved",
                            False,
                        ),

                    "evaluation":
                        content.get(
                            "evaluation",
                            {}
                        ),

                }
            )


        return evidence
