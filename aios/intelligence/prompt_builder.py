\
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PromptBuilderConfig:
    include_runtime: bool = True
    include_plan: bool = True
    include_evidence: bool = True
    include_tool_results: bool = True
    include_memory: bool = True
    include_governance: bool = True
    include_history: bool = True
    max_chars: int = 120000


class PromptSanitizer:

    @staticmethod
    def normalize(value):

        if value is None:
            return None

        if isinstance(value,(str,int,float,bool)):
            return value

        if isinstance(value,dict):
            return {
                str(k): PromptSanitizer.normalize(v)
                for k,v in value.items()
            }

        if isinstance(value,(list,tuple,set)):
            return [
                PromptSanitizer.normalize(x)
                for x in value
            ]

        if hasattr(value,"__dict__"):
            return PromptSanitizer.normalize(vars(value))

        return str(value)


class PromptBuilder:

    def __init__(self):

        self.config = PromptBuilderConfig()

    def build(
        self,
        capability,
        context,
    ):

        md = []

        md.append("# AIOS")
        md.append("Institutional AI Operating System")
        md.append("")

        md.append(f"Capability: {capability}")
        md.append("")

        self._append(
            md,
            "Decision",
            context.get("evidence_summary",{}).get("decision"),
        )

        self._append(
            md,
            "Candidate",
            context.get("evidence_summary",{}).get("candidate"),
        )

        self._append(
            md,
            "Capability Plan",
            context.get("capability_plan"),
        )

        self._append(
            md,
            "Tool Evidence",
            context.get("tool_evidence"),
        )

        self._append(
            md,
            "Tool Results",
            context.get("tool_results"),
        )

        self._append(
            md,
            "Evidence Summary",
            context.get("evidence_summary"),
        )

        self._append(
            md,
            "Runtime",
            context.get("runtime"),
        )

        self._append(
            md,
            "Workflow",
            context.get("workflow_plan"),
        )

        self._append(
            md,
            "Execution Graph",
            context.get("execution_graph"),
        )

        self._append(
            md,
            "Reasoning",
            context.get("reasoning"),
        )

        self._append(
            md,
            "Planning",
            context.get("plan"),
        )

        self._append(
            md,
            "Reflection",
            context.get("reflection"),
        )

        self._append(
            md,
            "Learning",
            context.get("learning"),
        )

        self._append(
            md,
            "Optimization",
            context.get("optimization"),
        )

        self._append(
            md,
            "Memory Snapshot",
            context.get("memory_snapshot"),
        )

        self._append(
            md,
            "Verification",
            context.get("verification"),
        )

        self._append(
            md,
            "Governance",
            context.get("governance"),
        )

        self._append(
            md,
            "Metrics",
            context.get("metrics"),
        )

        self._append(
            md,
            "Audit",
            context.get("audit"),
        )

        self._append(
            md,
            "Results",
            context.get("results"),
        )

        return {
            "system": (
                "You are AIOS. "
                "Use VERIFIED MCP evidence first. "
                "Never invent facts. "
                "If evidence exists, cite it. "
                "If evidence is empty, explicitly state that."
            ),
            "context":"\n".join(md)[:self.config.max_chars],
        }

    def _append(
        self,
        md,
        title,
        value,
    ):

        if not value:
            return

        md.append(f"## {title}")

        md.append(
            json.dumps(
                PromptSanitizer.normalize(value),
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )

        md.append("")
