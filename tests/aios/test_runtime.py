from aios.system import AIOSBootstrap
from aios.system.runtime import AIOSRuntime


def test_runtime_lifecycle():

    container = AIOSBootstrap().initialize()

    runtime = AIOSRuntime(
        container
    )

    state = runtime.start()

    assert state.status == "ready"

    runtime.shutdown()
