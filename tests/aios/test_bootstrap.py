from aios.system import AIOSBootstrap


def test_bootstrap_services():

    container = AIOSBootstrap().initialize()

    services = container.describe()

    required = [
        "event_bus",
        "memory_router",
        "memory_layers",
        "memory_intelligence",
        "project_manager",
        "supervisor",
        "runtime_daemon",
    ]

    for service in required:
        assert service in services
