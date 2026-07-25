class EvidenceGate:


    name = "evidence"


    def check(
        self,
        context,
    ):

        evidence = context.get(
            "evidence",
            {}
        )

        passed = evidence.get(
            "valid",
            False
        )


        result = {

            "gate":
                self.name,

            "passed":
                passed,

            "policy":
                context.get(
                    "policy",
                    {}
                ),

            "details": {

                "responses":
                    evidence.get(
                        "responses",
                        0
                    ),

                "artifacts":
                    evidence.get(
                        "artifacts",
                        0
                    ),

            },

        }


        if not passed:

            result["reason"] = (
                "Missing agent artifacts"
                if evidence.get("artifacts", 0) == 0
                else "Insufficient evidence"
            )


        return result



class SecurityGate:


    name = "security"


    def check(
        self,
        context,
    ):

        return {

            "gate":
                self.name,

            "passed":
                True,

            "policy":
                context.get(
                    "policy",
                    {}
                ),

        }



class DependencyGate:


    name = "dependency"


    def check(
        self,
        context,
    ):

        return {

            "gate":
                self.name,

            "passed":
                True,

            "policy":
                context.get(
                    "policy",
                    {}
                ),

        }



class RegressionGate:


    name = "regression"


    def check(
        self,
        context,
    ):

        return {

            "gate":
                self.name,

            "passed":
                True,

            "policy":
                context.get(
                    "policy",
                    {}
                ),

        }
