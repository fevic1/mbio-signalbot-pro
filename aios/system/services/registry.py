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

from aios.audit.logger import (
    AuditLogger,
)


class AIOSServiceRegistry:


    def build_core(self):

        services = {}


        #
        # Audit System
        #

        audit_logger = AuditLogger()


        services[
            "audit_logger"
        ] = audit_logger



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
        # Capability Registry
        #

        from aios.registry.capability_registry import (
            CapabilityRegistry,
        )


        capability_registry = CapabilityRegistry()


        services[
            "capability_registry"
        ] = capability_registry



        #
        # AIOS Capability Bootstrap
        #

        from aios.capabilities.models import (
            Capability,
        )


        def bootstrap_capabilities(
            registry,
        ):

            capabilities = [

                ("architecture_review", "system"),
                ("system_design", "system"),
                ("failure_analysis", "system"),

                ("market_analysis", "research"),
                ("strategy_review", "research"),
                ("backtesting", "research"),

                ("risk_review", "risk"),
                ("exposure_analysis", "risk"),
                ("capital_protection", "risk"),

                ("assumption_testing", "review"),
                ("failure_detection", "review"),

                ("validation", "verification"),
                ("quality_control", "verification"),

                ("research", "research"),
                ("information_analysis", "research"),

            ]


            for name, permission in capabilities:

                registry.register(
                    Capability(
                        name=name,
                        permission=permission,
                        description=
                            f"AIOS capability: {name}",
                    )
                )


        bootstrap_capabilities(
            capability_registry
        )



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
        # AIOS Expert Agent Bootstrap
        #

        from aios.agents.runtime import (
            AgentManager,
        )


        def bootstrap_agents(
            manager,
        ):

            agents = [

                (
                    "architect",
                    "system architect",
                    [
                        "architecture_review",
                        "system_design",
                        "failure_analysis",
                    ],
                ),

                (
                    "quant",
                    "quantitative analyst",
                    [
                        "market_analysis",
                        "strategy_review",
                        "backtesting",
                    ],
                ),

                (
                    "risk",
                    "risk analyst",
                    [
                        "risk_review",
                        "exposure_analysis",
                        "capital_protection",
                    ],
                ),

                (
                    "skeptic",
                    "critical reviewer",
                    [
                        "assumption_testing",
                        "failure_detection",
                    ],
                ),

                (
                    "verification",
                    "verification agent",
                    [
                        "validation",
                        "quality_control",
                    ],
                ),

                (
                    "research",
                    "research analyst",
                    [
                        "research",
                        "information_analysis",
                    ],
                ),

            ]


            for name, role, capabilities in agents:

                manager.create_agent(
                    name,
                    role,
                    capabilities,
                )



        bootstrap_agents(
            agent_manager
        )



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
            audit=audit_logger,
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
