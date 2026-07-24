from aios.runtime.health import RuntimeHealthMonitor


class FailedWorker:

    def status(self):

        return {
            "running": False,
            "thread_alive": False,
        }



def test_worker_failure_detected():

    health = RuntimeHealthMonitor(
        FailedWorker()
    ).check()

    assert health.status == "warning"
