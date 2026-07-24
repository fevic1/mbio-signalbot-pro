from aios.system import AIOSBootstrap
from aios.system.runtime import AIOSRuntime


def start():

    container = AIOSBootstrap().initialize()

    runtime = AIOSRuntime(
        container
    )

    state = runtime.start()

    return {
        "status": "started",
        "runtime": state.describe(),
        "container": container.describe(),
    }
