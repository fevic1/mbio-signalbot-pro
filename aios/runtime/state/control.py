from pathlib import Path


class RuntimeControlStore:


    def __init__(
        self,
        path=None,
    ):

        self.path = Path(
            path
            or ".aios/shutdown.request"
        )


    def request_shutdown(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            "shutdown"
        )


    def shutdown_requested(self):

        return self.path.exists()


    def clear(self):

        if self.path.exists():

            self.path.unlink()
