from aios.core.component import Component

import time
import logging

from .config import RuntimeConfig


logger = logging.getLogger(
    "aios.runtime"
)


class AIOSRuntimeDaemon(Component):


    def __init__(
        self,
        supervisor,
        config=None,
    ):

        self.supervisor = supervisor

        self.config = (
            config
            or RuntimeConfig()
        )

        self.running = False



    def run_once(
        self,
        projects,
    ):

        report = (
            self.supervisor
            .check_projects(
                projects
            )
        )


        if hasattr(
            report,
            "describe",
        ):

            output = report.describe()

        else:

            output = report


        logger.info(
            "Supervisor report: %s",
            output,
        )


        return output



    def start(
        self,
        projects,
    ):

        self.running = True


        while self.running:

            self.run_once(
                projects
            )


            time.sleep(
                self.config.interval_seconds
            )



    def stop(
        self,
    ):

        self.running = False
