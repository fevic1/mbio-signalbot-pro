class RollbackManager:


    def __init__(self):

        self.rollbacks = []



    def register(
        self,
        change_id,
        snapshot,
    ):

        self.rollbacks.append(
            {
                "change_id":
                    change_id,

                "snapshot":
                    snapshot,
            }
        )


    def rollback(
        self,
        change_id,
    ):

        for item in self.rollbacks:

            if item["change_id"] == change_id:

                return {

                    "rolled_back": True,

                    "snapshot":
                        item["snapshot"],

                }


        return {

            "rolled_back": False,

            "reason":
                "snapshot missing",

        }
