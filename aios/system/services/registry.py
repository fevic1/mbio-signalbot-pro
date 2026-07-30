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


    def build_core(self, container=None):

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
        # Decision Engine
        #

        from aios.decision.decision_engine import (
            DecisionEngine,
        )


        decision_engine = DecisionEngine(
            audit=audit_logger,
            event_bus=event_bus,
        )


        services[
            "decision_engine"
        ] = decision_engine




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


        #
        # Memory Manager Compatibility Layer
        #

        class MemoryManagerAdapter:

            def __init__(self, router):
                self.router = router


            def store(self, *args, **kwargs):
                if hasattr(self.router, "store"):
                    return self.router.store(
                        *args,
                        **kwargs,
                    )

                if hasattr(self.router, "append"):
                    return self.router.append(
                        *args,
                        **kwargs,
                    )

                return None


            def remember(
                self,
                memory_type=None,
                title=None,
                content=None,
                metadata=None,
                **kwargs,
            ):

                from aios.memory.models import (
                    MemoryRecord,
                    MemoryType,
                    MemoryImportance,
                    MemoryMetadata,
                )


                try:
                    resolved_type = MemoryType(
                        memory_type
                    )

                except Exception:
                    resolved_type = MemoryType.OPERATIONAL


                memory = MemoryRecord(
                    content={
                        "title": title or "AIOS Memory",
                        "content": content or "",
                    },
                    memory_type=resolved_type,
                    importance=MemoryImportance.NORMAL,
                    metadata=MemoryMetadata(
                        source="execution_executor",
                        tags=[],
                        confidence=1.0,
                        access_count=0,
                    ),
                )


                return self.router.store(
                    memory
                )


            def retrieve(self, *args, **kwargs):
                if hasattr(self.router, "retrieve"):
                    return self.router.retrieve(
                        *args,
                        **kwargs,
                    )

                return None


        memory_manager = MemoryManagerAdapter(
            memory_router
        )


        services[
            "memory_manager"
        ] = memory_manager




        repository = (
            memory_router.repository
            if hasattr(
                memory_router,
                "repository"
            )
            else memory_router
        )


        layer_registry = (
            MemoryLayerRegistry()
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
        # Neural Model Intelligence
        #

        from aios.neural_proxy.intelligence import (
            ModelIntelligence,
        )

        model_intelligence = ModelIntelligence()

        services[
            "model_intelligence"
        ] = model_intelligence



        #
        # Learning System
        #

        from aios.learning import (
            LearningCoordinator,
            ProviderFeedbackHandler,
        )


        learning = LearningCoordinator(
            memory_manager=memory_manager,
        )


        services[
            "learning"
        ] = learning


        provider_feedback = ProviderFeedbackHandler(
            event_bus=event_bus,
            learning=learning,
            model_intelligence=model_intelligence,
        )


        services[
            "provider_feedback"
        ] = provider_feedback



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
        # LLM Model Registry
        #

        from aios.llm.models import (
            ModelRegistry,
            LLMModel,
        )

        from aios.llm.router import (
            LLMRouter,
        )


        model_registry = ModelRegistry()


        model_registry.register(
            LLMModel(
                name="llama-3.1-8b-instant",
                provider="groq",
                capabilities=[
                    "research",
                    "market_analysis",
                    "information_analysis",
                ],
                cost_level="low",
                speed="fast",
            )
        )


        model_registry.register(
            LLMModel(
                name="openai/gpt-oss-20b:free",
                provider="openrouter",
                capabilities=[
                    "research",
                    "strategy_review",
                ],
                cost_level="low",
                speed="medium",
            )
        )


        llm_router = LLMRouter(
            model_registry
        )


        services[
            "model_registry"
        ] = model_registry


        services[
            "llm_router"
        ] = llm_router



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

                {
                    "name": "architecture_review",
                    "permission": "system",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

                {
                    "name": "system_design",
                    "permission": "system",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

                {
                    "name": "failure_analysis",
                    "permission": "system",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "medium",
                    },
                },

                {
                    "name": "market_analysis",
                    "permission": "research",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "medium",
                        "allowed_models": ["research"],
                    },
                    "timeout": 120,
                    "retry_limit": 3,
                },

                {
                    "name": "strategy_review",
                    "permission": "research",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "medium",
                    },
                },

                {
                    "name": "backtesting",
                    "permission": "research",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

                {
                    "name": "risk_review",
                    "permission": "risk",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "high",
                    },
                },

                {
                    "name": "exposure_analysis",
                    "permission": "risk",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "high",
                    },
                },

                {
                    "name": "capital_protection",
                    "permission": "risk",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "critical",
                    },
                },

                {
                    "name": "assumption_testing",
                    "permission": "review",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "medium",
                    },
                },

                {
                    "name": "failure_detection",
                    "permission": "review",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "medium",
                    },
                },

                {
                    "name": "validation",
                    "permission": "verification",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

                {
                    "name": "quality_control",
                    "permission": "verification",
                    "metadata": {
                        "requires_provider": False,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

                {
                    "name": "research",
                    "permission": "research",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "low",
                        "allowed_models": ["research"],
                    },
                    "timeout": 120,
                    "retry_limit": 3,
                },

                {
                    "name": "information_analysis",
                    "permission": "research",
                    "metadata": {
                        "requires_provider": True,
                        "memory_write": True,
                        "risk_level": "low",
                    },
                },

            ]


            for capability in capabilities:

                registry.register(
                    Capability(
                        name=capability["name"],
                        permission=capability["permission"],
                        description=
                            f"AIOS capability: {capability['name']}",
                        metadata=capability.get(
                            "metadata",
                            {},
                        ),
                        timeout=capability.get(
                            "timeout",
                            60,
                        ),
                        retry_limit=capability.get(
                            "retry_limit",
                            2,
                        ),
                    )
                )


        bootstrap_capabilities(
            capability_registry
        )




        #
        # Skill Registry
        #

        from aios.skills import (
            SkillRegistry,
            SkillLoader,
        )


        skill_registry = SkillRegistry()

        skill_loader = SkillLoader(
            skill_registry
        )

        skill_loader.load_builtin()


        services[
            "skill_registry"
        ] = skill_registry



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


        #
        # Task + Orchestration Compatibility Layer
        #

        from aios.runtime.task_manager import (
            TaskManager,
        )

        from aios.orchestrator.orchestrator import (
            AIOSOrchestrator,
        )


        #
        # Execution Planner
        #

        from aios.execution.planner import (
            ExecutionPlanner,
        )


        execution_planner = ExecutionPlanner()


        services[
            "execution_planner"
        ] = execution_planner



        #
        # Workflow Engine
        #

        from aios.workflows.execution_engine import (
            WorkflowEngine,
        )


        #
        # Workflow Engine
        # Delayed initialization
        #

        class WorkflowEngineProxy:

            def __init__(self, container):
                self.container = container
                self.engine = None


            def _init(self):

                if self.engine is None:

                    self.engine = WorkflowEngine(
                        self.container
                    )

                return self.engine


            async def execute(self, task):

                return await self._init().execute(
                    task
                )


        workflow_engine = WorkflowEngineProxy(
            container
        )


        services[
            "workflow_engine"
        ] = workflow_engine



        task_manager = TaskManager()


        services[
            "task_manager"
        ] = task_manager


        class AgentRegistryAdapter:

            def __init__(self, manager):
                self.manager = manager

            def list(self):
                return self.manager.describe()


        orchestrator = AIOSOrchestrator(
            task_manager=task_manager,
            registry=AgentRegistryAdapter(
                agent_manager
            ),
            decision_engine=None,
            workflow_engine=workflow_engine,
        )


        services[
            "orchestrator"
        ] = orchestrator


        #
        # Registry Compatibility Adapter
        #

        class AgentRegistryAdapter:

            def __init__(self, manager):
                self.manager = manager

            def list(self):
                return self.manager.describe()


        services[
            "registry"
        ] = AgentRegistryAdapter(
            agent_manager
        )


        #
        # AIOS Neural Proxy
        #

        from aios.neural_proxy import (
            NeuralProxyGateway,
        )

        from aios.neural_proxy.router import (
            NeuralProxyRouter,
        )

        from aios.neural_proxy.intelligence import (
            ModelIntelligence,
        )

        from aios.providers.router import (
            chat as provider_chat,
        )

        neural_proxy_router = NeuralProxyRouter(
            llm_router=services.get(
                "llm_router"
            ),
            provider_router=None,
            intelligence=model_intelligence,
        )


        neural_proxy = NeuralProxyGateway(
            router=neural_proxy_router,
            provider_chat=provider_chat,
            event_bus=event_bus,
        )


        services[
            "neural_proxy"
        ] = neural_proxy



        if container is not None:
            container.services.update(
                services
            )

        return services
