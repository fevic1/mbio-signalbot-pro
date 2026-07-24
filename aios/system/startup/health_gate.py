class StartupHealthGate:


    def check(
        self,
        container,
    ):

        checks = {
            "event_bus":
                container.get("event_bus") is not None,

            "memory":
                container.get("memory_router") is not None,

            "runtime_daemon":
                container.get("runtime_daemon") is not None,
        }


        return {
            "ready":
                all(checks.values()),

            "checks":
                checks,
        }
