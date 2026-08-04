from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParameterResult:
    arguments: dict
    missing: list[str]
    valid: bool


class ParameterPlanner:

    async def build(
        self,
        schema: dict,
        request,
    ) -> ParameterResult:

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        args = {}

        text = str(request).strip()

        for field in required:

            if field in properties:

                if field == "query":
                    args[field] = text

                elif field == "title":
                    args[field] = text

                elif field == "path":
                    if "/" in text or "." in text:
                        args[field] = text

                else:
                    args[field] = text

        missing = [
            field
            for field in required
            if field not in args
        ]

        return ParameterResult(
            arguments=args,
            missing=missing,
            valid=not missing,
        )
