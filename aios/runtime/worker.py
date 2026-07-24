import threading
import time

from aios.runtime.state import (
    RuntimeControlStore,
)


class RuntimeWorker:


    def __init__(
        self,
        daemon,
        projects=None,
    ):

        self.daemon = daemon

        self.projects = (
            projects
            or []
        )

        self.thread = None

        self.running = False

        self.control = RuntimeControlStore()

        self.watcher = None



    def start(self):

        if self.running:

            return


        self.running = True


        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()


        self.watcher = threading.Thread(
            target=self._watch_shutdown,
            daemon=True,
        )

        self.watcher.start()



    def _run(self):

        try:

            self.daemon.start(
                self.projects
            )

        finally:

            self.running = False



    def _watch_shutdown(self):

        while self.running:

            if self.control.shutdown_requested():

                self.stop()

                self.control.clear()

                break


            time.sleep(1)



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
