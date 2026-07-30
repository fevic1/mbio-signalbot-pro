import json

from aios.audit.migration import MigrationAnalyzer
from aios.audit.migration.models import MigrationManifest


MIGRATION_QUEUE = [
    {
        "component": "AgentRuntime",
        "canonical": "aios.agents.runtime.runtime",
        "owner": "agent-domain",
        "risk": "runtime",
        "status": "migration_pending",
        "implementations": [
            "aios.runtime.agent_runtime",
            "aios.agents.runtime",
        ],
    },
    {
        "component": "TaskEngine",
        "canonical": "aios.execution.task_engine",
        "owner": "execution-domain",
        "risk": "runtime",
        "status": "migration_pending",
        "implementations": [
            "aios.runtime.task_engine",
            "aios.execution.task_engine",
        ],
    },
    {
        "component": "PolicyEngine",
        "canonical": "aios.policy.engine",
        "owner": "policy-domain",
        "risk": "runtime",
        "status": "migration_pending",
        "implementations": [
            "aios.policy.engine",
            "aios.council.policy",
            "aios.runtime.policy_engine",
        ],
    },
    {
        "component": "WorkflowEngine",
        "canonical": "aios.workflows.engine",
        "owner": "workflow-domain",
        "risk": "runtime",
        "status": "migration_pending",
        "implementations": [
            "aios.workflows.engine",
            "aios.workflows.execution_engine",
            "aios.runtime.workflow_engine",
        ],
    },
    {
        "component": "PromptEngine",
        "canonical": "aios.prompts.engine",
        "owner": "prompt-domain",
        "risk": "review",
        "status": "migration_pending",
        "implementations": [
            "aios.prompts.engine",
            "aios.runtime.prompts",
        ],
    },
    {
        "component": "ToolRegistry",
        "canonical": "aios.tools.registry",
        "owner": "tool-domain",
        "risk": "review",
        "status": "migration_pending",
        "implementations": [
            "aios.tools.registry",
            "aios.runtime.tools",
        ],
    },
]


def run():

    analyzer = MigrationAnalyzer()

    reports = []

    for item in MIGRATION_QUEUE:

        manifest = MigrationManifest(**item)

        reports.append(
            analyzer.analyze(manifest)
        )

    print(
        json.dumps(
            reports,
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
