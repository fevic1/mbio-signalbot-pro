import json
import re
from time import perf_counter

from aios.intelligence.llm_adapter import LLMAdapter
from aios.providers.router import chat
from aios.providers.router import provider_pool
from aios.neural_proxy.protocol import AIOSRequest
from aios.capabilities.policy import CapabilityPolicyEngine
from aios.capabilities.errors import CapabilityExecutionError
from aios.events.models import AIOSDomainEvent

from .request import CapabilityRequest

class CapabilityExecutor:

    def __init__(
        self,
        system,
    ):
        self.system = system

        self.adapter = LLMAdapter(
            provider_pool,
            system,
        )

        self.policy = CapabilityPolicyEngine(
            provider_pool
        )

    def _get_capability_definition(self, name):

        registry = self.system.capability_registry

        if registry is None:
            raise CapabilityExecutionError(
                "Capability registry unavailable"
            )

        capability = registry.get(name)

        if capability is None:
            raise CapabilityExecutionError(
                f"Unknown capability: {name}"
            )

        return capability



    def _validate_capability_policy(
        self,
        capability,
    ):

        return self.policy.validate(
            capability
        )


    async def execute(
        self,
        request: CapabilityRequest,
    ):
        capability = self._get_capability_definition(
            request.capability
        )

        self._validate_capability_policy(
            capability
        )

        event_bus = getattr(
            self.system,
            "event_bus",
            None,
        )

        if event_bus:
            event_bus.publish(
                AIOSDomainEvent(
                    "execution.started",
                    source="capability_executor",
                    payload={
                        "capability": request.capability,
                        "retry_limit": request.retry_limit,
                    },
                )
            )

        last_error = None

        for attempt in range(
            request.retry_limit + 1
        ):
            try:
                result = await self._execute_once(
                    request,
                    attempt,
                )

                if event_bus:
                    event_bus.publish(
                        AIOSDomainEvent(
                            "execution.completed",
                            source="capability_executor",
                            payload={
                                "capability": request.capability,
                                "attempt": attempt,
                                "result": result,
                            },
                        )
                    )

                return result

            except Exception as error:
                last_error = error

                if event_bus:
                    event_bus.publish(
                        AIOSDomainEvent(
                            "execution.attempt_failed",
                            source="capability_executor",
                            payload={
                                "capability": request.capability,
                                "attempt": attempt,
                                "error": str(error),
                            },
                        )
                    )

        if event_bus:
            event_bus.publish(
                AIOSDomainEvent(
                    "execution.failed",
                    source="capability_executor",
                    payload={
                        "capability": request.capability,
                        "attempts": request.retry_limit + 1,
                        "error": str(last_error),
                        "success": False,
                    },
                )
            )

        raise CapabilityExecutionError(
            f"{request.capability}: {last_error}"
        ) from last_error

    async def _execute_once(
        self,
        request: CapabilityRequest,
        attempt: int,
    ):

        # Internal diagnostics are answered deterministically from verified
        # runtime state. The LLM must not override observed system evidence.
        request_context = (
            request.context
            if isinstance(request.context, dict)
            else {}
        )
        runtime_evidence = request_context.get("runtime_evidence")

        if isinstance(runtime_evidence, dict):
            recent_events = runtime_evidence.get("recent_event_types") or []
            event_count = int(
                runtime_evidence.get("persisted_event_count") or 0
            )

            telemetry_ok = all((
                runtime_evidence.get("event_bus"),
                runtime_evidence.get("event_persistence"),
                event_count > 0,
            ))
            learning_ok = all((
                runtime_evidence.get("learning_service"),
                runtime_evidence.get("learning_event_handler"),
                telemetry_ok,
            ))
            council_ok = all((
                runtime_evidence.get("council_manager"),
                runtime_evidence.get("improvement_review"),
            ))

            completed_seen = "execution.completed" in recent_events
            provider_health = runtime_evidence.get("provider_health") or {}
            healthy_providers = [
                name
                for name, healthy in provider_health.items()
                if healthy
            ]

            content = (
                f"AIOS learning telemetry is "
                f"{'operational' if learning_ok else 'not fully operational'}: "
                f"the event bus and persistent audit store are "
                f"{'active' if telemetry_ok else 'incomplete'}, with "
                f"{event_count} persisted events"
                f"{' and recent completed executions' if completed_seen else ''}. "
                f"Council review is "
                f"{'available' if council_ok else 'not fully available'} through "
                f"the council manager and improvement-review service. "
                f"Healthy AIOS providers: "
                f"{', '.join(healthy_providers) if healthy_providers else 'none'}."
            )

            return {
                "success": telemetry_ok,
                "capability": request.capability,
                "provider": "kernel",
                "model": "verified-runtime",
                "content": content,
                "latency": 0.0,
                "cost": 0.0,
                "attempt": attempt,
                "runtime_evidence": runtime_evidence,
            }

        prompt = self.adapter.build(
            request.capability,
            request,
        )

        mcp_client = None
        tools = []

        services = getattr(self.system, "services", None)
        if services:
            mcp_client = services.get("mcp_client")

        if mcp_client:
            tools = await mcp_client.list_tools()

        # Deterministic read-only market retrieval.
        market_context = None

        context_data = (
            request.context
            if isinstance(request.context, dict)
            else {}
        )
        current_query = str(
            context_data.get("message")
            or context_data.get("query")
            or ""
        ).strip()

        market_patterns = (
            r"\bbtc\b",
            r"\bbitcoin\b",
            r"\beth\b",
            r"\bethereum\b",
            r"\bsol\b",
            r"\bsolana\b",
            r"\bcrypto price\b",
            r"\bmarket price\b",
            r"\bmarket data\b",
            r"\bcurrent price\b",
            r"\bticker\b",
        )

        tool_names = {
            tool.get("name")
            for tool in tools
        }

        if (
            current_query
            and any(
                re.search(pattern, current_query.lower())
                for pattern in market_patterns
            )
            and "internet__get_crypto_prices" in tool_names
        ):
            detected = []

            symbol_terms = {
                "BTC": ("btc", "bitcoin"),
                "ETH": ("eth", "ethereum"),
                "SOL": ("sol", "solana"),
                "HYPE": ("hype", "hyperliquid"),
            }

            lowered_query = current_query.lower()

            for symbol, aliases in symbol_terms.items():
                if any(alias in lowered_query for alias in aliases):
                    detected.append(symbol)

            if not detected:
                detected = ["BTC", "ETH", "SOL"]

            try:
                market_context = await mcp_client.call_tool(
                    "internet__get_crypto_prices",
                    {"symbols": ",".join(detected)},
                )
            except Exception as error:
                market_context = {
                    "success": False,
                    "error": str(error),
                }

        # Fixed WebResearch workflow:
        # current-information requests are grounded before the LLM answers.
        research_context = None

        if (
            request.capability == "research"
            and mcp_client
        ):
            metadata = {}

            logger = __import__("logging").getLogger(__name__)
            logger.info(
                "AIOS RESEARCH: capability=%r context_type=%s context_keys=%s",
                request.capability,
                type(request.context).__name__,
                list(request.context.keys()) if isinstance(request.context, dict) else [],
            )

            if isinstance(request.context, dict):
                metadata = request.context.get("metadata", {})
                if not isinstance(metadata, dict):
                    metadata = {}

                query = str(
                    request.context.get("message")
                    or metadata.get("message")
                    or request.context.get("query")
                    or metadata.get("query")
                    or ""
                ).strip()
            else:
                query = str(
                    getattr(request.context, "message", "")
                    or getattr(request.context, "query", "")
                    or ""
                ).strip()
            tool_names = {tool.get("name") for tool in tools}

            research_terms = (
                "search",
                "look up",
                "look for",
                "latest",
                "current",
                "today",
                "news",
                "website",
                "web",
                "internet",
                "research",
            )

            if (
                query
                and any(term in query.lower() for term in research_terms)
                and "tavily__search_web" in tool_names
            ):
                try:
                    logger = __import__("logging").getLogger(__name__)
                    logger.info("AIOS RESEARCH: invoking tavily__search_web query=%r", query)

                    search_query = (
                        query
                        .replace("Give 3 factual bullets and cite the exact article URL for each.", "")
                        .replace("Give three factual bullets and cite the exact article URL for each.", "")
                        .replace("Give 3 factual bullets with exact article URLs.", "")
                        .replace("Give three factual bullets with exact article URLs.", "")
                        .strip()
                    )

                    lowered_search_query = search_query.lower()

                    if "look into" in lowered_search_query:
                        split_at = (
                            lowered_search_query.index("look into")
                            + len("look into")
                        )
                        focused_query = search_query[split_at:].strip()

                        if focused_query:
                            search_query = focused_query

                    if "news" in search_query.lower():
                        from datetime import datetime, timezone

                        current_date = datetime.now(timezone.utc).strftime("%B %Y")
                        search_query = (
                            f"{search_query} {current_date} "
                            "individual news articles"
                        )

                    raw_research_context = await mcp_client.call_tool(
                        "tavily__search_web",
                        {
                            "query": search_query,
                            "max_results": 8,
                        },
                    )

                    blocked_urls = {
                        "https://api.tavily.com/search",
                        "https://en.wikipedia.org/wiki/bitcoin",
                        "https://www.coindesk.com",
                        "https://www.cnbc.com/cryptoworld",
                        "https://news.bitcoin.com",
                        "https://finance.yahoo.com/markets/crypto",
                    }

                    blocked_path_terms = (
                        "/markets/crypto",
                        "/cryptoworld",
                        "/tag/",
                        "/tags/",
                        "/category/",
                        "/categories/",
                        "/topic/",
                        "/topics/",
                        "/search",
                    )

                    compact_results = []
                    for item in raw_research_context.get("results", []):
                        url = str(item.get("url", "")).strip()
                        normalized_url = url.rstrip("/").lower()

                        if not url.startswith(("http://", "https://")):
                            continue

                        if normalized_url in blocked_urls:
                            continue

                        if any(term in normalized_url for term in blocked_path_terms):
                            continue

                        # Prefer article-like URLs, not publication landing pages.
                        path_part = normalized_url.split("://", 1)[-1].split("/", 1)
                        path = "/" + path_part[1] if len(path_part) > 1 else "/"
                        if path == "/" or path.count("/") < 2:
                            continue

                        content = str(item.get("content", "")).strip()
                        if len(content) > 700:
                            content = content[:700].rsplit(" ", 1)[0] + "..."

                        compact_results.append(
                            {
                                "title": str(item.get("title", "")).strip(),
                                "url": url,
                                "content": content,
                                "published_date": item.get("published_date"),
                            }
                        )

                    research_context = {
                        "success": raw_research_context.get("success", True),
                        "query": search_query,
                        "results": compact_results[:3],
                    }

                    if not research_context["results"]:
                        research_context = {
                            "success": False,
                            "query": search_query,
                            "results": [],
                            "error": "No exact article URLs found from search results.",
                        }

                    logger.info(
                        "AIOS RESEARCH: compact Tavily results=%s",
                        research_context,
                    )
                except Exception as error:
                    research_context = {
                        "success": False,
                        "error": str(error),
                        "results": [],
                    }

        aios_request_context = str(prompt["context"])

        if market_context is not None:
            aios_request_context += (
                "\n\nVERIFIED LIVE MARKET DATA:\n"
                + json.dumps(
                    market_context,
                    ensure_ascii=False,
                    default=str,
                )
                + "\nUse these exact values. Include the source URL "
                  "and retrieval time. Never claim live-data limitations "
                  "when success is true."
            )

        if research_context is not None:
            aios_request_context += (
                "\n\nVERIFIED WEB RESEARCH RESULTS:\n"
                + json.dumps(
                    research_context,
                    ensure_ascii=False,
                    default=str,
                )
            )

        # Retrieval is deterministic. The LLM synthesizes but cannot
        # autonomously invoke arbitrary tools.
        tools = []

        aios_request = AIOSRequest(
            capability=request.capability,
            messages=[
                {
                    "role": "system",
                    "content": prompt["system"],
                },
                {
                    "role": "user",
                    "content": aios_request_context,
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get(
                            "inputSchema",
                            {"type": "object"},
                        ),
                    },
                }
                for tool in tools
            ],
            constraints={
                "temperature": 0.2,
                "max_tokens": (
                    768
                    if request.capability == "research"
                    else 384
                ),
                "allowed_models": (
                    self._get_capability_definition(
                        request.capability
                    )
                    .metadata
                    .get("allowed_models")
                ),
            },
        )

        start = perf_counter()

        allowed_models = (
            self._get_capability_definition(
                request.capability
            )
            .metadata
            .get("allowed_models")
        )

        selected_model = None

        if allowed_models:

            llm_router = getattr(
                self.system,
                "llm_router",
                None,
            )

            if llm_router:

                selected_model = llm_router.select_model(
                    request.capability,
                    allowed_models=allowed_models,
                )

        if selected_model:
            aios_request.constraints["model"] = selected_model.name

        response = await self.system.neural_proxy.execute(
            aios_request
        )

        for _ in range(3):
            raw = response.metadata.get("raw", {})
            message = (
                raw.get("choices", [{}])[0]
                .get("message", {})
            )
            tool_calls = message.get("tool_calls") or []

            if not tool_calls or not mcp_client:
                break

            aios_request.messages.append(message)

            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name")
                arguments = function.get("arguments", "{}")

                try:
                    arguments = json.loads(arguments)
                except Exception:
                    arguments = {}

                try:
                    tool_result = await mcp_client.call_tool(
                        tool_name,
                        arguments,
                    )
                except Exception as error:
                    tool_result = {
                        "success": False,
                        "error": str(error),
                    }

                aios_request.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "name": tool_name,
                    "content": json.dumps(
                        tool_result,
                        default=str,
                    ),
                })

            response = await self.system.neural_proxy.execute(
                aios_request
            )

        latency = perf_counter() - start

        content = response.content

        parsed = {}

        if isinstance(content, str):
            cleaned = re.sub(
                r"```json\\s*|```",
                "",
                content,
            )

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start != -1 and end > start:
                try:
                    parsed = json.loads(
                        cleaned[start:end + 1]
                    )
                except Exception:
                    parsed = {}

        content = response.content

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                pass

        final_content = parsed or content

        if isinstance(final_content, dict):

            confidence = final_content.get(
                "confidence"
            )

            if confidence is not None:

                if confidence == 0:
                    final_content["confidence"] = 0.5

                elif confidence > 1:
                    final_content["confidence"] = confidence / 100

        return {
            "success": True,
            "capability": request.capability,
            "provider": response.provider,
            "model": response.model,
            "selected_model": (
                selected_model.name
                if selected_model
                else None
            ),
            "content": final_content,
            "latency": latency,
            "cost": 0.0,
            "attempt": attempt,
        }
