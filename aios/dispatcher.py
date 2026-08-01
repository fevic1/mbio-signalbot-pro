import logging
from typing import Any, Dict, Tuple

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest


logger = logging.getLogger(__name__)


class AIOSDispatcher:
    """
    Central AIOS Kernel Dispatcher.

    Responsibilities:
    - command routing
    - task classification
    - agent selection
    - capability execution
    - response normalization

    This layer sits between the chat interface and AIOS execution.
    """

    def __init__(self, system: Any):
        self.system = system
        self.executor = CapabilityExecutor(system)

    async def dispatch(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        message = str(
            payload.get("message", "")
        ).strip()

        if not message:
            return self._build_result(
                capability="system",
                content="No message provided.",
                success=False,
            )

        if message.startswith("/"):
            return await self._handle_command(
                message
            )

        agent, capability = self._classify_task(
            message
        )

        lowered_message = message.lower()
        research_overrides = (
            "look into",
            "research",
            "search",
            "latest",
            "news",
            "etf",
            "fund",
        )

        if any(
            term in lowered_message
            for term in research_overrides
        ):
            agent = "research"
            capability = "research"

        context = await self._build_context(
            message,
            agent,
            payload.get("history", []),
        )

        request = CapabilityRequest(
            capability=capability,
            context=context,
        )

        result = await self.executor.execute(
            request
        )

        return self._format_response(
            result,
            agent,
        )

    async def _handle_command(
        self,
        command: str,
    ) -> Dict[str, Any]:

        cmd = command.split()[0].lower()

        if cmd == "/status":

            return self._build_result(
                capability="status",
                content=(
                    "AIOS Enterprise Kernel\n\n"
                    "Status: ONLINE\n"
                    "Runtime: READY\n"
                    "Mode: Guarded Autonomous"
                ),
            )

        if cmd == "/agents":

            manager = self.system.services.get(
                "agent_manager"
            )

            if manager and hasattr(manager, "describe"):
                agents = manager.describe()

                if isinstance(agents, list):
                    content = "AIOS Workforce Agents\\n\\n"

                    for i, agent in enumerate(agents, 1):
                        content += (
                            f"{i}. {agent.get('name', 'unknown').title()}\\n"
                            f"   Role: {agent.get('role', 'unknown')}\\n"
                            f"   Capabilities: {', '.join(agent.get('capabilities', []))}\\n\\n"
                        )
                else:
                    content = str(agents)
            else:
                content = "Agent registry unavailable."

            return self._build_result(
                capability="agents",
                content=str(content),
            )

        if cmd == "/council":

            council = self.system.services.get(
                "council_manager"
            )

            return self._build_result(
                capability="council",
                content=str(
                    council
                    if council
                    else "Council unavailable."
                ),
            )

        if cmd == "/help":

            return self._build_result(
                capability="help",
                content=(
                    "AIOS Commands:\n\n"
                    "/status\n"
                    "/agents\n"
                    "/council\n"
                    "/help"
                ),
            )

        request = CapabilityRequest(
            capability="reasoning",
            context={
                "message": (
                    f"Interpret command: {command}"
                )
            },
        )

        result = await self.executor.execute(
            request
        )

        return self._format_response(
            result,
            "reasoning",
        )

    def _classify_task(
        self,
        message: str,
    ) -> Tuple[str, str]:

        text = message.lower()

        if any(
            key in text
            for key in [
                "risk",
                "exposure",
                "drawdown",
                "stoploss",
                "margin",
                "liquidation",
            ]
        ):
            return (
                "risk",
                "risk_analysis",
            )

        # Current-information intent must win before market terms like
        # bitcoin/btc/price, otherwise news searches become market_analysis.
        if any(
            key in text
            for key in [
                "research",
                "search",
                "look up",
                "look for",
                "find",
                "fetch",
                "latest",
                "current",
                "today",
                "news",
                "internet",
                "website",
                "web",
                "investigate",
            ]
        ):
            return (
                "research",
                "research",
            )

        if any(
            key in text
            for key in [
                "market",
                "btc",
                "bitcoin",
                "eth",
                "price",
                "chart",
                "indicator",
                "quant",
            ]
        ):
            return (
                "quant",
                "market_analysis",
            )

        if any(
            key in text
            for key in [
                "verify",
                "validate",
                "check",
                "test",
            ]
        ):
            return (
                "verification",
                "verification",
            )

        if any(
            key in text
            for key in [
                "architecture",
                "system",
                "infrastructure",
                "pipeline",
                "design",
            ]
        ):
            return (
                "architect",
                "reasoning",
            )

        return (
            "reasoning",
            "reasoning",
        )

    async def _build_context(
        self,
        message: str,
        agent: str,
        history: Any = None,
    ) -> Dict[str, Any]:

        conversation_history = []

        if isinstance(history, list):
            for item in history[-20:]:
                if not isinstance(item, dict):
                    continue

                role = str(
                    item.get("role")
                    or item.get("type")
                    or ""
                ).lower()

                if role == "ai":
                    role = "assistant"

                if role not in {"user", "assistant"}:
                    continue

                content = str(item.get("content", "")).strip()
                if not content:
                    continue

                conversation_history.append({
                    "role": role,
                    "content": content[:4000],
                })

        context = {
            "message": message,
            "conversation_history": conversation_history,
            "target_agent": agent,
            "aios_mode": "dispatcher",
        }

        mcp_registry = self.system.services.get(
            "mcp_registry"
        )

        if mcp_registry:

            context["mcp_tools"] = await (
                mcp_registry.get_all_tools()
            )

            context["mcp_servers"] = [
                server.server_id
                for server in await (
                    mcp_registry.get_all_servers()
                )
            ]

        diagnostic_terms = (
            "status",
            "health",
            "operational",
            "telemetry",
            "learning",
            "event",
            "council",
            "provider",
            "runtime",
            "system diagnostic",
        )

        if any(
            term in message.lower()
            for term in diagnostic_terms
        ):
            services = getattr(
                self.system,
                "services",
                {},
            ) or {}

            event_bus = services.get(
                "event_bus"
            )

            event_history = (
                event_bus.get_history()
                if event_bus
                and hasattr(event_bus, "get_history")
                else []
            )

            recent_event_types = [
                event.get("event_type")
                for event in event_history[-12:]
                if isinstance(event, dict)
            ]

            persistence = services.get(
                "event_persistence"
            )

            persisted_events = (
                persistence.load()
                if persistence
                and hasattr(persistence, "load")
                else []
            )

            try:
                from aios.providers.manager import provider_manager

                provider_health = (
                    provider_manager.health()
                )
            except Exception:
                provider_health = {}

            context["runtime_evidence"] = {
                "kernel": "online",
                "event_bus": event_bus is not None,
                "learning_service": services.get("learning") is not None,
                "learning_event_handler": services.get(
                    "learning_event_handler"
                ) is not None,
                "council_manager": services.get(
                    "council_manager"
                ) is not None,
                "improvement_review": services.get(
                    "improvement_review"
                ) is not None,
                "event_persistence": persistence is not None,
                "persisted_event_count": len(persisted_events),
                "recent_event_types": recent_event_types,
                "provider_health": provider_health,
            }

        return context

    def _format_response(
        self,
        result: Dict[str, Any],
        agent: str,
    ) -> Dict[str, Any]:

        content = result.get(
            "content"
        )

        if isinstance(content, dict):

            content = (
                content.get("summary")
                or content.get("message")
                or content.get("reasoning")
                or content.get("analysis")
                or content.get("response")
            )

            if content is None:
                import json
                content = json.dumps(
                    result.get("content"),
                    indent=2,
                )

        elif isinstance(content, list):

            import json
            content = json.dumps(
                content,
                indent=2,
            )

        if content is None:
            content = ""

        content = str(content)

        return {
            "success": result.get(
                "success",
                True,
            ),
            "capability": result.get(
                "capability"
            ),
            "agent": agent,
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "content": content,
            "latency": result.get(
                "latency"
            ),
            "cost": result.get(
                "cost",
                0.0,
            ),
            "attempt": result.get(
                "attempt",
                0,
            ),
        }

    def _build_result(
        self,
        capability: str,
        content: Any,
        success: bool = True,
    ) -> Dict[str, Any]:

        return {
            "success": success,
            "capability": capability,
            "agent": "system_kernel",
            "provider": "kernel",
            "model": "internal",
            "content": (
                __import__("json").dumps(
                    content,
                    indent=2,
                )
                if isinstance(content, (dict, list))
                else str(content)
            ),
            "latency": 0,
            "cost": 0,
            "attempt": 0,
        }
