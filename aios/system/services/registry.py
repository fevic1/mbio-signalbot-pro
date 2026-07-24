from aios.events import EventBus


class AIOSServiceRegistry:


    def build_core(self):

        services = {}


        event_bus = EventBus()


        services[
            "event_bus"
        ] = event_bus


        return services
