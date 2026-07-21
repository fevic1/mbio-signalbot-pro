class RetryPolicy:

    def __init__(
        self,
        max_attempts=3
    ):
        self.max_attempts = max_attempts


    def should_retry(
        self,
        attempts,
        error=None
    ):

        if attempts >= self.max_attempts:
            return False

        return True


    def status(
        self,
        attempts
    ):

        return {
            "attempts": attempts,
            "remaining":
                max(
                    0,
                    self.max_attempts - attempts
                )
        }
