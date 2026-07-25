from aios.runtime.state import (
    RuntimeStateStore,
)



def status():

    store = RuntimeStateStore()

    state = store.load()


    if state is None:

        return {
            "status":
            "not_running"
        }


    return state
