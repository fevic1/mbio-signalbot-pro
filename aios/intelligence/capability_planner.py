import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)

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
    "open", "read", "explain", "describe", "list", "search", "fetch"
}


def extract_value(param_name: str, request: str) -> str | None:
    """Pure heuristic extractor for tool parameters."""
    lname = param_name.lower()
    request = request.strip()
    
    if not request:
        return None
        
    if any(k in lname for k in ("path", "file", "filename", "filepath")):
        match = re.search(r'[a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+', request)
        if match:
            return match.group(0)
        words = request.split()
        if words and '/' in words[-1]:
            return words[-1]
        return None

    if any(k in lname for k in ("symbol", "ticker", "token", "coin", "asset")):
        words = request.split()
        for w in words:
            clean = w.strip(".,!?;:\"'()[]{}")
            if clean.isupper() and 2 <= len(clean) <= 5:
                return clean
        if words:
            return words[-1].strip(".,!?;:\"'()[]{}").upper()
        return None

    if any(k in lname for k in ("title", "topic", "subject", "article", "page", "name")):
        words = [w.strip(".,!?;:\"'()[]{}") for w in request.split() if w.lower() not in STOP_WORDS]
        if words:
            return " ".join(words[-2:]) if len(words) >= 2 else words[-1]
        return request

    if any(k in lname for k in ("query", "search", "keyword", "text", "prompt", "input")):
        return request

    return request


@dataclass(slots=True)
class ParameterValidationResult:
    success: bool
    arguments: dict[str, Any]
    missing_required: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass(slots=True)
class CapabilityCandidate:
    server: str
    tool: str
    score: float


class CapabilityPlanner:

    async def plan(self, registry, request: str):
        request = str(request).lower()
        candidates = []
        all_tools = await registry.get_all_tools() if hasattr(registry, "get_all_tools") else {}

        for server, tools in all_tools.items():
            for tool in tools.keys():
                score = max(
                    SequenceMatcher(None, request, tool.lower()).ratio(),
                    SequenceMatcher(None, request, server.lower()).ratio(),
                )
                keywords = (tool + " " + server).lower()
                for token in request.split():
                    if token in keywords:
                        score += 0.15
                candidates.append(CapabilityCandidate(server, tool, round(score, 3)))

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    async def select(self, registry, request, limit=5):
        planner = ParameterPlanner()
        planned = await self.plan(registry, request)
        result = []

        for c in planned[:limit]:
            validation = await planner.validate_and_build(
                registry, c.server, c.tool, request
            )
            
            step = {
                "server": c.server,
                "tool": c.tool,
                "score": c.score,
                "arguments": validation.arguments,
            }
            
            if not validation.success:
                step["validation_error"] = validation.error
                
            result.append(step)

        return result


class ParameterPlanner:

    async def validate_and_build(self, registry, server: str, tool: str, request: str) -> ParameterValidationResult:
        schema = await registry.get_tool_schema_async(server, tool)
        
        if not schema:
            return ParameterValidationResult(
                success=False, arguments={}, error="Schema not available"
            )

        input_schema = schema.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        if not properties:
            return ParameterValidationResult(success=True, arguments={})

        request_str = str(request).strip()
        args = {}
        missing = []

        for name in properties:
            value = extract_value(name, request_str)
            if value is not None:
                args[name] = value

        for req in required:
            if req not in args:
                missing.append(req)

        if missing:
            return ParameterValidationResult(
                success=False,
                arguments=args,
                missing_required=missing,
                error=f"Missing required arguments: {missing}"
            )

        return ParameterValidationResult(success=True, arguments=args)
