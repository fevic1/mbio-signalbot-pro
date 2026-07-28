from aios.runtime.kernel import RuntimeKernel
from aios.supervisor import HealthState
from aios.runtime.state import RuntimeState


class Bootstrap:

    def __init__(self, kernel: RuntimeKernel | None = None):
        self.kernel = kernel or RuntimeKernel()

    def initialize(self):
        self.kernel.metadata.version = self.kernel.version
        self.kernel.capabilities.enable('workflow_engine')
        self.kernel.capabilities.enable('task_engine')
        self.kernel.capabilities.enable('tool_registry')
        self.kernel.capabilities.enable('prompt_engine')
        self.kernel.capabilities.enable('agent_runtime')
        self.kernel.capabilities.enable('policy_engine')
        self.kernel.capabilities.enable('supervisor')
        self.kernel.capabilities.enable('semantic_memory')
        self.kernel.features.enable('runtime')
        self.kernel.features.enable('diagnostics')
        self.kernel.features.enable('lifecycle')
        self.kernel.features.enable('events')
        self.kernel.features.enable('plugins')
        self.kernel.features.enable('extensions')
        self.kernel.features.enable('metadata')
        self.kernel.features.enable('introspection')

        self.kernel.resources.register('task_engine', self.kernel.task_engine)
        self.kernel.resources.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.resources.register('tool_registry', self.kernel.tool_registry)
        self.kernel.resources.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.resources.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.resources.register('policy_engine', self.kernel.policy_engine)
        self.kernel.resources.register('supervisor', self.kernel.supervisor)
        self.kernel.resources.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.services.register('task_engine', self.kernel.task_engine)
        self.kernel.services.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.services.register('tool_registry', self.kernel.tool_registry)
        self.kernel.services.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.services.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.services.register('policy_engine', self.kernel.policy_engine)
        self.kernel.services.register('supervisor', self.kernel.supervisor)
        self.kernel.services.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.modules.register('task_engine', self.kernel.task_engine)
        self.kernel.modules.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.modules.register('tool_registry', self.kernel.tool_registry)
        self.kernel.modules.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.modules.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.modules.register('policy_engine', self.kernel.policy_engine)
        self.kernel.modules.register('supervisor', self.kernel.supervisor)
        self.kernel.modules.register('semantic_memory', self.kernel.semantic_memory)

        from aios.runtime.extensions import RuntimeExtension

        self.kernel.extensions.register(
            RuntimeExtension(
                name="runtime",
            )
        )

        self.kernel.packages.register('task_engine', self.kernel.task_engine)
        self.kernel.packages.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.packages.register('tool_registry', self.kernel.tool_registry)
        self.kernel.packages.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.packages.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.packages.register('policy_engine', self.kernel.policy_engine)
        self.kernel.packages.register('supervisor', self.kernel.supervisor)
        self.kernel.packages.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.providers.register('task_engine', self.kernel.task_engine)
        self.kernel.providers.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.providers.register('tool_registry', self.kernel.tool_registry)
        self.kernel.providers.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.providers.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.providers.register('policy_engine', self.kernel.policy_engine)
        self.kernel.providers.register('supervisor', self.kernel.supervisor)
        self.kernel.providers.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.drivers.register('task_engine', self.kernel.task_engine)
        self.kernel.drivers.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.drivers.register('tool_registry', self.kernel.tool_registry)
        self.kernel.drivers.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.drivers.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.drivers.register('policy_engine', self.kernel.policy_engine)
        self.kernel.drivers.register('supervisor', self.kernel.supervisor)
        self.kernel.drivers.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.adapters.register('task_engine', self.kernel.task_engine)
        self.kernel.adapters.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.adapters.register('tool_registry', self.kernel.tool_registry)
        self.kernel.adapters.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.adapters.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.adapters.register('policy_engine', self.kernel.policy_engine)
        self.kernel.adapters.register('supervisor', self.kernel.supervisor)
        self.kernel.adapters.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.connectors.register('task_engine', self.kernel.task_engine)
        self.kernel.connectors.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.connectors.register('tool_registry', self.kernel.tool_registry)
        self.kernel.connectors.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.connectors.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.connectors.register('policy_engine', self.kernel.policy_engine)
        self.kernel.connectors.register('supervisor', self.kernel.supervisor)
        self.kernel.connectors.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.endpoints.register('task_engine', self.kernel.task_engine)
        self.kernel.endpoints.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.endpoints.register('tool_registry', self.kernel.tool_registry)
        self.kernel.endpoints.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.endpoints.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.endpoints.register('policy_engine', self.kernel.policy_engine)
        self.kernel.endpoints.register('supervisor', self.kernel.supervisor)
        self.kernel.endpoints.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.hooks.register('task_engine', self.kernel.task_engine)
        self.kernel.hooks.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.hooks.register('tool_registry', self.kernel.tool_registry)
        self.kernel.hooks.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.hooks.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.hooks.register('policy_engine', self.kernel.policy_engine)
        self.kernel.hooks.register('supervisor', self.kernel.supervisor)
        self.kernel.hooks.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.policies.register('task_engine', self.kernel.task_engine)
        self.kernel.policies.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.policies.register('tool_registry', self.kernel.tool_registry)
        self.kernel.policies.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.policies.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.policies.register('policy_engine', self.kernel.policy_engine)
        self.kernel.policies.register('supervisor', self.kernel.supervisor)
        self.kernel.policies.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.configuration.register('task_engine', self.kernel.task_engine)
        self.kernel.configuration.register('workflow_engine', self.kernel.workflow_engine)
        self.kernel.configuration.register('tool_registry', self.kernel.tool_registry)
        self.kernel.configuration.register('prompt_engine', self.kernel.prompt_engine)
        self.kernel.configuration.register('agent_runtime', self.kernel.agent_runtime)
        self.kernel.configuration.register('policy_engine', self.kernel.policy_engine)
        self.kernel.configuration.register('supervisor', self.kernel.supervisor)
        self.kernel.configuration.register('semantic_memory', self.kernel.semantic_memory)

        self.kernel.registry.register('resources', self.kernel.resources)
        self.kernel.registry.register('services', self.kernel.services)
        self.kernel.registry.register('modules', self.kernel.modules)
        self.kernel.registry.register('extensions', self.kernel.extensions)
        self.kernel.registry.register('packages', self.kernel.packages)
        self.kernel.registry.register('providers', self.kernel.providers)
        self.kernel.registry.register('drivers', self.kernel.drivers)
        self.kernel.registry.register('adapters', self.kernel.adapters)
        self.kernel.registry.register('connectors', self.kernel.connectors)
        self.kernel.registry.register('endpoints', self.kernel.endpoints)
        self.kernel.registry.register('hooks', self.kernel.hooks)
        self.kernel.registry.register('policies', self.kernel.policies)
        self.kernel.registry.register('configuration', self.kernel.configuration)
        self.kernel.state = RuntimeState.INITIALIZING
        self.kernel.status.state = self.kernel.state
        self.kernel.metadata.start()
        self.kernel.state = RuntimeState.STOPPED
        self.kernel.status.state = self.kernel.state
        self.kernel.status.started = False

        self.kernel.lifecycle.emit(
            self.kernel.lifecycle.latest().phase.CREATED if False else __import__("aios.runtime.lifecycle").runtime.lifecycle.LifecyclePhase.INITIALIZING,
            "runtime",
        )
        self.kernel.extensions.initialize(self.kernel)

        for name, service in self.kernel.services().items():
            self.kernel.supervisor.register(name, service)
            self.kernel.supervisor.update(
                name,
                HealthState.HEALTHY,
                "Initialized",
            )
        self.kernel.lifecycle.emit(
            __import__("aios.runtime.lifecycle").runtime.lifecycle.LifecyclePhase.STARTED,
            "runtime",
        )
        self.kernel.state = RuntimeState.RUNNING
        self.kernel.status.state = self.kernel.state
        self.kernel.status.started = True
        self.kernel.status.services = len(self.kernel.services())
        self.kernel.status.agents = len(self.kernel.agent_runtime)
        self.kernel.status.tasks = len(self.kernel.task_engine)
        self.kernel.status.plugins = len(self.kernel.plugins)
        self.kernel.status.extensions = len(self.kernel.extensions)
        return self.kernel

    def shutdown(self):
        self.kernel.state = RuntimeState.STOPPING
        self.kernel.status.state = self.kernel.state
        self.kernel.metadata.stop()
        self.kernel.lifecycle.emit(
            __import__("aios.runtime.lifecycle").runtime.lifecycle.LifecyclePhase.STOPPING,
            "runtime",
        )
        self.kernel.extensions.shutdown(self.kernel)

        for name in list(self.kernel.services()):
            self.kernel.supervisor.unregister(name)

        self.kernel.lifecycle.emit(
            __import__("aios.runtime.lifecycle").runtime.lifecycle.LifecyclePhase.STOPPED,
            "runtime",
        )

    def health(self):
        return {
            name: self.kernel.supervisor.status(name)
            for name in self.kernel.services()
        }
