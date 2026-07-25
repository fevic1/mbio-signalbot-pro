class FailureDetector:


    def __init__(self):

        self.failures = []



    def check(
        self,
        condition,
        message,
    ):

        if condition:

            return {
                "healthy": True,
                "message": "ok",
            }


        failure = {
            "healthy": False,
            "message": message,
        }


        self.failures.append(
            failure
        )


        return failure



    def report(
        self,
    ):

        return {
            "failures":
                self.failures,
            "healthy":
                len(self.failures) == 0,
        }
