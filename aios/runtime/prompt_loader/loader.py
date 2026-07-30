"""
AIOS Prompt Loader Runtime.

Compiles governance, role prompts, permissions,
and memory boundaries into deterministic agent context.
"""

from pathlib import Path
from datetime import datetime, timezone
import hashlib

from .models import (
    AgentExecutionContext,
    AgentPermissions,
    MemoryConfig,
    PermissionLevel,
    PromptInheritanceChain,
)

from .resolver import (
    PromptResolver,
)


class PromptLoader:

    def __init__(self, root_dir=None):
        self.resolver = PromptResolver(root_dir)


    def _read(self, path: Path) -> str:
        return path.read_text(
            encoding="utf-8"
        )


    def _permission(
        self,
        value
    ):

        normalized = str(value).replace(
            "_",
            " "
        ).strip()

        mapping = {
            "Level0": PermissionLevel.LEVEL_0_OBSERVE,
            "Level 0": PermissionLevel.LEVEL_0_OBSERVE,

            "Level1": PermissionLevel.LEVEL_1_SUGGEST,
            "Level 1": PermissionLevel.LEVEL_1_SUGGEST,

            "Level2": PermissionLevel.LEVEL_2_EXECUTE_SAFE,
            "Level 2": PermissionLevel.LEVEL_2_EXECUTE_SAFE,

            "Level3": PermissionLevel.LEVEL_3_PRODUCTION,
            "Level 3": PermissionLevel.LEVEL_3_PRODUCTION,
        }

        if normalized not in mapping:
            raise ValueError(
                f"Unknown permission level: {value}"
            )

        return mapping[normalized]


    def assemble_context(
        self,
        agent_name: str
    ):

        constitution = (
            self.resolver.constitution()
        )

        security = (
            self.resolver.security_rules()
        )

        reliability = (
            self.resolver.reliability_rules()
        )

        role = (
            self.resolver.agent_prompt(
                agent_name
            )
        )

        registry = (
            self.resolver.registry_config(
                agent_name
            )
        )


        permissions = AgentPermissions(
            level=self._permission(
                registry.get(
                    "permission",
                    "Level 1"
                )
            ),
            allowed_tools=registry.get(
                "allowed_tools",
                []
            ),
            forbidden_tools=registry.get(
                "forbidden_tools",
                []
            ),
            requires_human_approval=True,
        )


        memory_cfg = registry.get(
            "memory",
            {}
        )

        memory = MemoryConfig(
            read_paths=memory_cfg.get(
                "read",
                [
                    ".aios/memory/"
                ]
            ),
            write_paths=memory_cfg.get(
                "write",
                [
                    ".aios/decisions/"
                ]
            ),
        )


        inheritance = PromptInheritanceChain(
            constitution_path=str(
                constitution
            ),
            security_rules_path=str(
                security
            ),
            reliability_rules_path=str(
                reliability
            ),
            agent_role_path=str(
                role
            ),
        )


        system_prompt = self._compile(
            [
                constitution,
                security,
                reliability,
                role,
            ],
            agent_name,
            permissions,
            memory,
        )


        return AgentExecutionContext(
            agent_name=agent_name,
            role_title=registry.get(
                "role_title",
                agent_name
            ),
            inheritance=inheritance,
            permissions=permissions,
            memory=memory,
            system_prompt=system_prompt,
            metadata={
                "prompt_hash": hashlib.sha256(
                    system_prompt.encode()
                ).hexdigest(),
                "loaded_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
            is_verified=True,
        )


    def _compile(
        self,
        files,
        agent_name,
        permissions,
        memory,
    ):

        sections = []

        for path in files:
            sections.append(
                f"\n===== {path} =====\n"
            )
            sections.append(
                self._read(path)
            )


        sections.append(
            "\n===== RUNTIME CONTROL =====\n"
        )

        sections.append(
            f"AGENT: {agent_name}"
        )

        sections.append(
            f"PERMISSION: {permissions.level.value}"
        )

        sections.append(
            "MEMORY READ: "
            +
            ",".join(memory.read_paths)
        )

        sections.append(
            "MEMORY WRITE: "
            +
            ",".join(memory.write_paths)
        )

        return "\n".join(sections)
