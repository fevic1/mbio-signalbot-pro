from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParameterValidationResult:
    success: bool
    arguments: dict[str, Any]
    missing_required: list[str] = field(default_factory=list)
    error: str | None = None


class ParameterPlanner:

    async def validate_and_build(
        self,
        registry,
        server: str,
        tool: str,
        request: str,
    ) -> ParameterValidationResult:

        schema = await registry.get_tool_schema_async(
            server,
            tool,
        )

        if not schema:
            return ParameterValidationResult(
                success=False,
                arguments={},
                error="Tool schema unavailable",
            )

        input_schema = schema.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        args = {}

        for name, definition in properties.items():

            value = self._extract(
                name,
                definition,
                request,
            )

            if value is not None:
                args[name] = value

        missing = [
            field
            for field in required
            if field not in args
        ]

        return ParameterValidationResult(
            success=not missing,
            arguments=args,
            missing_required=missing,
            error=None if not missing else f"Missing required arguments: {missing}",
        )

    def _extract(
        self,
        name: str,
        definition: dict,
        request: str,
    ):

        text = request.strip()

        lname = name.lower()

        desc = definition.get(
            "description",
            "",
        ).lower()

        key = f"{lname} {desc}"

        if any(x in key for x in (
            "query",
            "search",
            "keyword",
        )):
            return text

        if any(x in key for x in (
            "title",
            "article",
            "page",
            "topic",
        )):
            return text

        if any(x in key for x in (
            "symbol",
            "ticker",
            "coin",
            "asset",
            "token",
        )):
            m = re.search(r"\b[A-Z]{2,10}\b", request)

            if m:
                return m.group(0)

        if any(x in key for x in (
            "path",
            "file",
            "filename",
        )):

            m = re.search(
                r"[\w/\-.]+\.[A-Za-z0-9]+",
                request,
            )

            if m:
                return m.group(0)

        return None
