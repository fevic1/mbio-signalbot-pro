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




        #
        # Agent Runtime System
        #

        from aios.agents.runtime import (
            AgentManager,
        )

        from aios.agents.workspace import (
            WorkspaceManager,
        )

        from aios.agents.communication import (
            AgentCommunicationManager,
        )


        agent_manager = AgentManager()

        workspace_manager = WorkspaceManager()

        communication_manager = (
            AgentCommunicationManager(
                event_bus
            )
        )


        services[
            "agent_manager"
        ] = agent_manager


        services[
            "workspace_manager"
        ] = workspace_manager


        services[
            "communication_manager"
        ] = communication_manager



        #
        # Council Governance System
        #

        from aios.council import (
            CouncilManager,
        )


        council_manager = CouncilManager(
            event_bus=event_bus,
            agent_manager=agent_manager,
            communication=communication_manager,
        )


        services[
            "council_manager"
        ] = council_manager




        #
        # Autonomous Operations
        #

        try:

            from aios.projects.autonomous.manager import (
                AutonomousProjectManager,
            )

            from aios.projects.autonomous import (
                ProjectHealthMonitor,
            )

            from aios.projects.autonomous.decision import (
                ProjectDecisionEngine,
            )


            project_manager = (
                AutonomousProjectManager(
                    ProjectHealthMonitor(),
                    ProjectDecisionEngine(),
                )
            )


            services[
                "project_manager"
            ] = project_manager


        except ImportError:

            pass



        try:

            from aios.supervisor import (
                AutonomousSupervisor,
            )


            supervisor = (
                AutonomousSupervisor(
                    project_manager
                )
            )


            services[
                "supervisor"
            ] = supervisor


        except ImportError:

            pass



        try:

            from aios.runtime import (
                AIOSRuntimeDaemon,
            )


            runtime_daemon = (
                AIOSRuntimeDaemon(
                    supervisor
                )
            )


            services[
                "runtime_daemon"
            ] = runtime_daemon


        except ImportError:

            pass


        return services
