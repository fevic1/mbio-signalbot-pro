from aios.runtime.health import RuntimeHealthMonitor


class Worker:

    def status(self):

        return {
            "running": True,
            "thread_alive": True,
        }



def test_runtime_health():

    health = RuntimeHealthMonitor(
        Worker()
    ).check()

    assert health.status == "ok"
