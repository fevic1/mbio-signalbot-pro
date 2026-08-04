from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because", "but", "and",
    "or", "if", "while", "about", "against", "up", "down", "me", "my",
    "we", "our", "you", "your", "he", "him", "his", "she", "her", "it",
    "its", "they", "them", "their", "what", "which", "who", "whom", "this",
    "that", "these", "those", "am", "tell", "give", "show", "find", "get",
    "open", "read", "explain", "describe", "list", "search", "fetch",
    "summarize", "summary", "article", "wikipedia", "document", "create",
    "maker", "creator", "price", "current", "btc"
}


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

        schema = await registry.get_tool_schema_async(server, tool)

        if not schema:
            return self._infer_and_extract(tool, request)

        input_schema = schema.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        # If schema is present but properties are empty (minimal schema), infer from tool name
        if not properties:
            return self._infer_and_extract(tool, request)

        args = {}
        for name, definition in properties.items():
            value = self._extract(name, definition, request)
            if value is not None:
                args[name] = value

        missing = [f for f in required if f not in args]

        return ParameterValidationResult(
            success=not missing,
            arguments=args,
            missing_required=missing,
            error=None if not missing else f"Missing required arguments: {missing}",
        )

    def _infer_and_extract(self, tool: str, request: str) -> ParameterValidationResult:
        """Handles minimal schemas by inferring parameter name from tool name."""
        tool_lower = tool.lower()
        
        if any(k in tool_lower for k in ("search", "find", "lookup", "query")):
            param_name = "query"
        elif any(k in tool_lower for k in ("summary", "article", "page", "topic", "about")):
            param_name = "title"
        elif any(k in tool_lower for k in ("read", "load", "document", "file", "open")):
            param_name = "path"
        else:
            return ParameterValidationResult(
                success=False, arguments={}, error="Cannot infer parameter for minimal schema"
            )

        # Create a dummy definition to pass to _extract
        dummy_def = {"description": param_name}
        value = self._extract(param_name, dummy_def, request)

        if value:
            return ParameterValidationResult(success=True, arguments={param_name: value})
        
        return ParameterValidationResult(
            success=False, arguments={}, error=f"Failed to extract {param_name}"
        )

    def _extract(self, name: str, definition: dict, request: str) -> str | None:
        """Pure heuristic extractor with entity normalization."""
        text = request.strip()
        if not text:
            return None

        lname = name.lower()
        desc = definition.get("description", "").lower()
        key = f"{lname} {desc}"

        # Path Extraction: regex for file paths
        if any(x in key for x in ("path", "file", "filename", "filepath")):
            m = re.search(r'[\w/\-.]+\.[A-Za-z0-9]+', text)
            return m.group(0) if m else None

        # Symbol/Ticker Extraction: uppercase words
        if any(x in key for x in ("symbol", "ticker", "coin", "asset", "token")):
            m = re.search(r"\b[A-Z]{2,10}\b", text)
            return m.group(0) if m else None

        # Title/Topic Extraction: strip stop words and intent verbs
        if any(x in key for x in ("title", "article", "page", "topic", "subject", "name")):
            return self._extract_title(text)

        # Query/Search Extraction: return cleaned text
        if any(x in key for x in ("query", "search", "keyword", "text", "prompt", "input")):
            return self._extract_query(text)

        return None

    def _extract_title(self, text: str) -> str:
        """Extracts the core entity by removing stop words and intent verbs."""
        words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.lower() not in STOP_WORDS]
        if not words:
            return text
        # Take the last 1-2 words as the likely title/entity
        return " ".join(words[-2:]) if len(words) >= 2 else words[-1]

    def _extract_query(self, text: str) -> str:
        """Returns the query, stripping common leading intent phrases."""
        # Simple cleanup: remove "search for ", "find ", etc. if they exist at the start
        cleaned = re.sub(r'^(search\s+for|find|lookup|look\s+up)\s+', '', text, flags=re.IGNORECASE)
        return cleaned.strip() if cleaned.strip() else text
