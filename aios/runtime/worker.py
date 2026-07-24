import threading


class RuntimeWorker:


    def __init__(
        self,
        daemon,
    ):

        self.daemon = daemon

        self.thread = None

        self.running = False



    def start(self):

        if self.running:

            return


        self.running = True


        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()



    def _run(self):

        try:

            self.daemon.run()

        finally:

            self.running = False



    def stop(self):

        if not self.running:

            return


        self.running = False


        if hasattr(
            self.daemon,
            "stop"
        ):

            self.daemon.stop()



    def status(self):

        return {
            "running":
            self.running,

            "thread_alive":
            self.thread.is_alive()
            if self.thread
            else False,
        }
