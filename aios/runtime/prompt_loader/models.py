from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any


class PermissionLevel(Enum):
    LEVEL_0_OBSERVE = "Level 0"
    LEVEL_1_SUGGEST = "Level 1"
    LEVEL_2_EXECUTE_SAFE = "Level 2"
    LEVEL_3_PRODUCTION = "Level 3"


@dataclass
class MemoryConfig:
    read_paths: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)


@dataclass
class AgentPermissions:
    level: PermissionLevel
    allowed_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    requires_human_approval: bool = True


@dataclass
class PromptInheritanceChain:
    constitution_path: str
    security_rules_path: str
    reliability_rules_path: str
    agent_role_path: str


@dataclass
class AgentExecutionContext:

    agent_name: str
    role_title: str

    inheritance: PromptInheritanceChain

    permissions: AgentPermissions

    memory: MemoryConfig

    system_prompt: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    is_verified: bool = False
