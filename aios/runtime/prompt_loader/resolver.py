from pathlib import Path
import os
import yaml


class PromptResolverError(Exception):
    pass


class PromptResolver:

    def __init__(self, root_dir=None):

        self.root_dir = Path(
            root_dir or os.getcwd()
        )

        self.governance = (
            self.root_dir /
            ".aios" /
            "governance"
        )

        self.prompts = (
            self.root_dir /
            ".aios" /
            "prompts" /
            "agents"
        )

        self.registry = (
            self.root_dir /
            ".aios" /
            "agents" /
            "registry.yaml"
        )


    def require(self, path):

        if not path.exists():
            raise PromptResolverError(
                f"Missing required file: {path}"
            )

        return path


    def constitution(self):

        return self.require(
            self.governance /
            "llm_operating_constitution.md"
        )


    def security_rules(self):

        return self.require(
            self.governance /
            "security_operating_rules.md"
        )


    def reliability_rules(self):

        return self.require(
            self.governance /
            "reliability_rules.md"
        )


    def agent_prompt(self, name):

        return self.require(
            self.prompts /
            f"{name}.md"
        )


    def registry_config(self, name):

        with open(
            self.registry,
            encoding="utf-8"
        ) as f:

            data = yaml.safe_load(f)

        agents = data.get(
            "agents",
            {}
        )

        if name not in agents:
            raise PromptResolverError(
                f"{name} not registered"
            )

        return agents[name]
