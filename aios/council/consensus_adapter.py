from .evidence import EvidenceEvaluator


class ConsensusAdapter:


    def __init__(self):

        self.evidence = EvidenceEvaluator()



    def build(
        self,
        council_report,
    ):

        evidence = self.evidence.evaluate(
            council_report
        )

        responses = (
            council_report.get(
                "responses",
                []
            )
        )


        approved = True


        if not responses:

            approved = False


        return {

            "validator": {

                "valid":
                    approved,

                "issues":
                    []
                    if approved
                    else [
                        "No agent responses"
                    ],

            },


            "critic": {

                "approved":
                    approved,

                "score":
                    1.0 if approved else 0.0,

            },


            "policy": {

                "allowed":
                    approved,

                "issues":
                    [],

            },


            "evidence":
                evidence,

        }
