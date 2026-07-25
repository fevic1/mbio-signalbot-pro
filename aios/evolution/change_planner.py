class ChangePlanner:


    def create_change_request(
        self,
        proposal,
        review,
    ):

        if not review.get(
            "approved",
            False,
        ):

            return {

                "created": False,

                "reason":
                    "proposal not approved",

            }


        governance = review.get(
            "governance",
            {}
        )


        return {

            "created": True,

            "component":
                proposal["pattern"].get(
                    "source"
                ),

            "reason":
                proposal["pattern"].get(
                    "message"
                ),

            "rollback_available":
                True,

            "proposal_id":
                proposal["proposal_id"],

            "governance":
                governance,

        }


    def submit(
        self,
        change_request,
        change_manager,
    ):

        if not change_request.get(
            "created",
            False,
        ):

            return {
                "created": False,
                "reason": "invalid change request",
            }


        change = change_manager.create(
            change_request["component"],
            change_request["reason"],
            change_request["rollback_available"],
        )


        change["proposal_id"] = (
            change_request.get(
                "proposal_id"
            )
        )


        change["governance"] = (
            change_request.get(
                "governance",
                {}
            )
        )


        return change
