class IntegrityHealth:


    def __init__(
        self,
        guards,
    ):

        self.guards = guards



    def check(self):

        results = [

            guard.check()

            for guard in self.guards

        ]


        return {

            "healthy":

                all(
                    item["passed"]
                    for item in results
                ),

            "results":
                results,

        }
