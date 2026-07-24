from aios.runtime.state import (
    RuntimeControlStore,
)



def stop():

    control = RuntimeControlStore()

    control.request_shutdown()


    return {
        "status":
        "shutdown_requested"
    }
