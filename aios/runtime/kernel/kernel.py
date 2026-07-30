from aios.runtime.supervisor import Supervisor
from aios.runtime.memory_intelligence import MemoryIntelligence
from aios.events.bus import EventBus
from aios.governance.permissions import PermissionManager
from aios.governance.approval import ApprovalManager
from aios.governance.audit import AuditLogger
from aios.control.approval_workflow import ApprovalWorkflow
from aios.governance.runtime import GovernanceGateway
from aios.control.audit import RuntimeAudit
from aios.runtime.dag.graph import ExecutionGraph
from aios.runtime.prompts import PromptEngine
from aios.runtime.policy_engine import PolicyEngine as RuntimePolicyEngine
from aios.runtime.tools import ToolRegistry
from aios.runtime.dag import ExecutionGraph
from aios.runtime.task_engine import TaskEngine
from aios.runtime.workflow_engine import WorkflowEngine as RuntimeWorkflowEngine
from aios.agents.runtime import AgentRuntime
from aios.execution.task_engine import TaskEngine
from aios.execution import ExecutionOrchestrator
from aios.risk import RiskEngine
from aios.execution.audit import ExecutionAuditHandler
from aios.memory.semantic import SemanticMemory
from aios.policy import PolicyEngine as DomainPolicyEngine
from aios.prompts import PromptEngine
from aios.supervisor import Supervisor
from aios.tools import ToolRegistry
from aios.workflows.engine import WorkflowEngine as WorkflowExecutionEngine
from aios.runtime.container import ServiceContainer
from aios.runtime.metadata import RuntimeMetadata
from aios.runtime.capabilities import RuntimeCapabilities
from aios.runtime.features import RuntimeFeatures
from aios.runtime.resources import RuntimeResources
from aios.runtime.modules import RuntimeModules
from aios.runtime.packages import RuntimePackageRegistry
from aios.runtime.providers import RuntimeProviderRegistry
from aios.runtime.drivers import RuntimeDriverRegistry
from aios.runtime.adapters import RuntimeAdapterRegistry
from aios.runtime.connectors import RuntimeConnectorRegistry
from aios.runtime.endpoints import RuntimeEndpointRegistry
from aios.runtime.hooks import RuntimeHookRegistry
from aios.runtime.policies import RuntimePolicyRegistry
from aios.runtime.configuration import RuntimeConfigurationRegistry
from aios.runtime.registry import RuntimeRegistryStore
from aios.runtime.status import RuntimeStatus
from aios.runtime.plugins import RuntimePluginRegistry
from aios.runtime.lifecycle import LifecycleManager
from aios.runtime.extensions import ExtensionManager


class RuntimeKernel:

    def __init__(self):
        self.version = "1.0.0"
        self.metadata = RuntimeMetadata()
        self.capabilities = RuntimeCapabilities()
        self.features = RuntimeFeatures()
        self.resources = RuntimeResources()
        self.modules = RuntimeModules()
        self.packages = RuntimePackageRegistry()
        self.providers = RuntimeProviderRegistry()
        self.drivers = RuntimeDriverRegistry()
        self.adapters = RuntimeAdapterRegistry()
        self.connectors = RuntimeConnectorRegistry()
        self.endpoints = RuntimeEndpointRegistry()
        self.hooks = RuntimeHookRegistry()
        self.policies = RuntimePolicyRegistry()
        self.configuration = RuntimeConfigurationRegistry()
        self.registry = RuntimeRegistryStore()
        self.status = RuntimeStatus()
        self.lifecycle = LifecycleManager()
        self.plugins = RuntimePluginRegistry()
        self.container = ServiceContainer()
        self.extensions = ExtensionManager()
        self.task_engine = TaskEngine()
        self.workflow_engine = WorkflowExecutionEngine(self.task_engine)
        self.tool_registry = ToolRegistry()
        self.prompt_engine = PromptEngine()
        self.agent_runtime = AgentRuntime()
        self.policy_engine = RuntimePolicyEngine()
        self.supervisor = Supervisor()
        self.semantic_memory = SemanticMemory()
        self.memory_intelligence = MemoryIntelligence()
        self.event_bus = EventBus()
        self.permission_manager = PermissionManager()
        self.approval_manager = ApprovalManager()
        self.approval_workflow = ApprovalWorkflow()
        self.audit_logger = AuditLogger()

        self.governance_gateway = GovernanceGateway(
            self.permission_manager,
            self.approval_manager,
            self.audit_logger,
        )
        self.audit = RuntimeAudit()

        self.execution_audit_handler = ExecutionAuditHandler(
            self.event_bus,
            self.audit,
        )
        self.execution_graph = ExecutionGraph()
        self.risk_engine = RiskEngine()

        self.execution_orchestrator = ExecutionOrchestrator(
            event_bus=self.event_bus,
            governance=self.governance_gateway,
            risk_engine=self.risk_engine,
        )
        self.register_services()


    @property
    def services(self):
        return self.container

    def register_services(self):
        services = {
            "task_engine": self.task_engine,
            "workflow_engine": self.workflow_engine,
            "tool_registry": self.tool_registry,
            "prompt_engine": self.prompt_engine,
            "agent_runtime": self.agent_runtime,
            "policy_engine": self.policy_engine,
            "supervisor": self.supervisor,
            "semantic_memory": self.semantic_memory,
            "memory_intelligence": self.memory_intelligence,
            "execution_graph": self.execution_graph,
            "execution_orchestrator": self.execution_orchestrator,
            "event_bus": self.event_bus,
            "metadata": self.metadata,
            "capabilities": self.capabilities,
            "features": self.features,
            "resources": self.resources,
            "modules": self.modules,
            "packages": self.packages,
            "providers": self.providers,
            "drivers": self.drivers,
            "adapters": self.adapters,
            "connectors": self.connectors,
            "endpoints": self.endpoints,
            "hooks": self.hooks,
            "policies": self.policies,
            "configuration": self.configuration,
            "registry": self.registry,
            "status": self.status,
            "plugins": self.plugins,
            "lifecycle": self.lifecycle,
            "permission_manager": self.permission_manager,
            "approval_manager": self.approval_manager,
            "approval_workflow": self.approval_workflow,
            "governance_gateway": self.governance_gateway,
            "audit": self.audit,
        }

        self.container.clear()
        for name, service in services.items():
            self.container.register(name, service)

        return services

    def get(self, name):
        return self.services()[name]
