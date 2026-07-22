from time import sleep


def retry(operation, retries=3, delay=1.0):
    """
    Retry a callable before giving up.
    """

    last_error = None

    for attempt in range(retries):
        try:
            return operation()
        except Exception as exc:
            last_error = exc

            if attempt < retries - 1:
                sleep(delay)

    raise last_error
