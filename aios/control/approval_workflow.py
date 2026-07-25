class ApprovalWorkflow:


    def __init__(
        self,
        control_audit=None,
    ):

        self.control_audit = control_audit



    def approve(
        self,
        change,
        governance,
        metadata=None,
    ):

        if not governance.get(
            "passed",
            False,
        ):

            return {

                "approved": False,

                "reason":
                    "governance failed",

            }


        change["approved"] = True


        result = {

            "approved": True,

            "change":
                change,

            "governance":
                governance,

        }


        if metadata:

            result.update(
                metadata
            )


        if self.control_audit:

            self.control_audit.record_change(
                change,
                result,
            )


        return result
