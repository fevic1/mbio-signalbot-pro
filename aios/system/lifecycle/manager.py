from .models import LifecycleState


class LifecycleManager:


    def __init__(
        self,
        container,
    ):

        self.container = container

        self.state = LifecycleState(
            "created"
        )



    def start(self):

        self.state = LifecycleState(
            "ready"
        )

        return self.state



    def shutdown(self):

        self.state = LifecycleState(
            "shutdown"
        )

        return self.state



    def status(self):

        return self.state.describe()
