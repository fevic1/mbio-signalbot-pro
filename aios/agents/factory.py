from .models import Agent


class DynamicAgentFactory:

    ROLE_MAP = {
        "Research": ("Researcher", ["search", "reason", "summarize"]),
        "Architecture": ("Architect", ["plan", "reason"]),
        "Implementation": ("Coder", ["code", "edit_file", "execute_command"]),
        "Testing": ("Tester", ["run_tests", "analyze_logs"]),
        "Deployment": ("Operator", ["execute_command", "call_api"]),
        "Monitoring": ("Observer", ["analyze_logs", "search"]),
        "Maintenance": ("Maintainer", ["edit_file", "run_tests"]),
    }

    def build(self, milestone):

        role, capabilities = self.ROLE_MAP.get(
            milestone.name,
            ("Worker", []),
        )

        return Agent(
            role=role,
            capabilities=capabilities,
            metadata={
                "milestone": milestone.id,
            },
        )
