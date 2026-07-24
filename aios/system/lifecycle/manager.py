from .models import LifecycleState


class LifecycleManager:


    def __init__(
        self,
        container,
        publisher=None,
    ):

        self.container = container

        self.publisher = publisher

        self.state = LifecycleState(
            "created"
        )



    def start(self):

        if self.publisher:

            self.publisher.publish_starting()


        self.state = LifecycleState(
            "ready"
        )


        if self.publisher:

            self.publisher.publish_ready()


        return self.state



    def shutdown(self):

        if self.publisher:

            self.publisher.publish_shutdown()


        self.state = LifecycleState(
            "shutdown"
        )

        return self.state



    def status(self):

        return self.state.describe()
