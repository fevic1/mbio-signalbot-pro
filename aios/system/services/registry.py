from aios.events import EventBus

from aios.memory import (
    PersistentMemoryRouter,
)

from aios.memory.intelligence import (
    MemoryIntelligenceEngine,
)

from aios.memory.layers import (
    MemoryLayerRegistry,
)


class AIOSServiceRegistry:


    def build_core(self):

        services = {}


        #
        # Event System
        #

        event_bus = EventBus()

        services[
            "event_bus"
        ] = event_bus



        #
        # Memory System
        #

        memory_router = (
            PersistentMemoryRouter(
                "aios_memory.db"
            )
        )


        services[
            "memory_router"
        ] = memory_router



        repository = (
            memory_router.repository
            if hasattr(
                memory_router,
                "repository"
            )
            else memory_router
        )


        layer_registry = (
            MemoryLayerRegistry(
                repository
            )
        )


        services[
            "memory_layers"
        ] = layer_registry



        memory_intelligence = (
            MemoryIntelligenceEngine(
                memory_router,
                layer_registry,
            )
        )


        services[
            "memory_intelligence"
        ] = memory_intelligence



        return services
