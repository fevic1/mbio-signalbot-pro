from .container import AIOSContainer

from aios.events import EventBus

from aios.integrity.health import IntegrityHealth
from aios.integrity.architecture import ArchitectureGuard
from aios.integrity.dependency import DependencyGuard
from aios.integrity.memory import MemoryGuard



from core.mcp_registry import mcp_registry


class AIOSBootstrap:


    def __init__(self):

        self.container = AIOSContainer()



    def boot(self):
        return self.initialize()



    async def initialize_async(self):

        from core.mcp_registry import mcp_registry

        mcp_registry.discover_servers()
        await mcp_registry.register_runtime_tools_async()

        self.container.register(
            "mcp_registry",
            mcp_registry,
        )

        return self.initialize(skip_mcp=True)


    def initialize(self, skip_mcp=False):

        integrity = IntegrityHealth(
            [
                ArchitectureGuard(),
                DependencyGuard(),
                MemoryGuard(),
            ]
        )


        health = integrity.check()


        if not health["healthy"]:

            raise RuntimeError(
                {
                    "aios_integrity_failed":
                        health
                }
            )


        from .services.registry import (
            AIOSServiceRegistry
        )


        registry = AIOSServiceRegistry()

        if not skip_mcp:

            mcp_registry.discover_servers()
            mcp_registry.register_runtime_tools()

            self.container.register(
                "mcp_registry",
                mcp_registry,
            )
            self.container.mcp_registry = mcp_registry

        services = registry.build_core(self.container)


        for name, service in services.items():

            self.container.register(
                name,
                service
            )


        from aios.workflows.multi_agent import (
            MultiAgentWorkflow,
        )


        self.container.register(
            "multi_agent_workflow",
            MultiAgentWorkflow(
                self.container
            ),
        )




        from aios.integrity.capability import CapabilityGuard


        agent_manager = self.container.get(
            "agent_manager"
        )


        capability_result = CapabilityGuard(
            agent_manager
        ).check()


        if not capability_result["passed"]:

            raise RuntimeError(
                {
                    "aios_capability_failed":
                        capability_result
                }
            )


        def capability_result_check():

            return capability_result


        from aios.monitoring.metrics import (
            MetricsCollector
        )

        from aios.monitoring.events import (
            MonitoringEvents
        )

        from aios.monitoring.health import (
            SystemHealth
        )


        metrics = MetricsCollector()

        monitoring_events = MonitoringEvents(
            metrics
        )


        system_health = SystemHealth(
            [
                integrity.check,
                capability_result_check,
            ]
        )


        self.container.register(
            "metrics",
            metrics,
        )


        self.container.register(
            "monitoring_events",
            monitoring_events,
        )


        self.container.register(
            "system_health",
            system_health,
        )


        from aios.operations.deployment_guard import (
            DeploymentGuard
        )

        from aios.operations.runtime_policy import (
            RuntimePolicy
        )

        from aios.operations.config_validation import (
            ConfigValidator
        )

        from aios.operations.incident_manager import (
            IncidentManager
        )


        deployment_guard = DeploymentGuard()

        runtime_policy = RuntimePolicy()

        config_validator = ConfigValidator()

        incident_manager = IncidentManager()


        self.container.register(
            "deployment_guard",
            deployment_guard,
        )


        self.container.register(
            "runtime_policy",
            runtime_policy,
        )


        self.container.register(
            "config_validator",
            config_validator,
        )


        self.container.register(
            "incident_manager",
            incident_manager,
        )


        runtime_result = runtime_policy.validate(
            {
                "governance_enabled": True,
            }
        )


        if not runtime_result["allowed"]:

            raise RuntimeError(
                {
                    "aios_runtime_policy_failed":
                        runtime_result
                }
            )


        deployment_result = deployment_guard.check(
            {
                "approved": True,

                "rollback_available": True,
            }
        )


        if not deployment_result["passed"]:

            raise RuntimeError(
                {
                    "aios_deployment_failed":
                        deployment_result
                }
            )


        from aios.control.change_manager import (
            ChangeManager
        )

        from aios.control.approval_workflow import (
            ApprovalWorkflow
        )

        from aios.control.rollback_manager import (
            RollbackManager
        )

        from aios.control.audit_replay import (
            AuditReplay
        )

        from aios.control.audit import (
            ControlAudit
        )


        self.container.register(
            "change_manager",
            ChangeManager(),
        )


        control_audit = ControlAudit(
            self.container.get(
                "audit_logger"
            )
        )


        self.container.register(
            "control_audit",
            control_audit,
        )


        self.container.register(
            "approval_workflow",
            ApprovalWorkflow(
                control_audit
            ),
        )


        self.container.register(
            "rollback_manager",
            RollbackManager(),
        )


        self.container.register(
            "audit_replay",
            AuditReplay(),
        )


        return self.container



    def describe(self):

        return self.container.describe()
