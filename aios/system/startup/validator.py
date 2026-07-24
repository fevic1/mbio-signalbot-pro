class StartupValidator:


    REQUIRED_SERVICES = [
        "event_bus",
        "memory_router",
        "memory_layers",
        "memory_intelligence",
        "project_manager",
        "supervisor",
        "runtime_daemon",
    ]


    def validate(
        self,
        container,
    ):

        services = container.describe()


        missing = [
            service
            for service in self.REQUIRED_SERVICES
            if service not in services
        ]


        return {
            "ready":
                len(missing) == 0,

            "missing":
                missing,

            "services":
                services,
        }
