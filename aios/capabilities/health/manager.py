from .models import CapabilityHealth


class CapabilityHealthManager:


    def __init__(self):

        self.health = {}


    def get(
        self,
        capability,
    ):

        if capability not in self.health:

            self.health[capability] = CapabilityHealth(
                capability
            )

        return self.health[capability]


    def record_success(
        self,
        capability,
        latency,
        cost,
    ):

        self.get(
            capability
        ).record_success(
            latency,
            cost,
        )


    def record_failure(
        self,
        capability,
    ):

        self.get(
            capability
        ).record_failure()


    def snapshot(self):

        return self.health
