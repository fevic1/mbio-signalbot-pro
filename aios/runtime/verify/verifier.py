from aios.runtime.runtime.runtime import Runtime

from .checks import (
    check_kernel,
    check_supervisor,
    check_lifecycle,
    check_events,
)


class RuntimeVerifier:

    def __init__(self):
        self.runtime = Runtime()
        self.kernel = self.runtime.start()

    def verify(self):

        return {
            "kernel": check_kernel(self.kernel),
            "supervisor": check_supervisor(self.kernel),
            "lifecycle": check_lifecycle(self.kernel),
            "events": check_events(self.kernel),
        }
