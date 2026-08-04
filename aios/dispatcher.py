import logging
import re
from typing import Any, Dict, Tuple



FAST_AGENT_RULES = {
    "coder": (
        "code","python","typescript","javascript","react","vue","fastapi",
        "bug","fix","debug","refactor","compile","build","docker",
        "sql","database","api","endpoint","ui","frontend","backend",
        "dashboard","qt","grid","dca","trade","execution","patch"
    ),
    "research": (
        "research","market","macro","bitcoin","btc","eth","sol",
        "analysis","news","report","paper","whitepaper"
    ),
    "documentation": (
        "document","docs","readme","markdown","wiki"
    ),
    "security": (
        "security","cve","vulnerability","exploit","audit"
    ),
    "devops": (
        "deploy","kubernetes","docker-compose","nginx","systemd","ci","cd"
    ),
    "reviewer": (
        "review","pr","merge","approve"
    ),
}

def fast_route(message: str):
    msg = (message or "").lower()

    best = "conversation"
    score = 0

    for agent, words in FAST_AGENT_RULES.items():
        s = sum(1 for w in words if w in msg)
        if s > score:
            best = agent
            score = s

    return best

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest
from aios.intelligence.compact_context import CompactContextBuilder
from aios.intelligence.super_context import SuperContextBuilder
from aios.intelligence.attachment_context import AttachmentContextBuilder
from aios.events.models import AIOSDomainEvent
from aios.policy.project_scope import resolve_project_scope


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
        self.context_builder = CompactContextBuilder(
            max_items=8,
            max_chars=5000,
        )
        self.super_context_builder = SuperContextBuilder()

        self.attachment_builder = AttachmentContextBuilder(
            max_context_chars=60000,
        )

    async def dispatch(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        attachments = payload.get("attachments") or []

        message = str(
            payload.get("message", "")
        ).strip()

        if not message and attachments:
            message = "Review and summarize the attached text."

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

        if self._needs_intent_clarification(message):
            return self._build_result(
                capability="reasoning",
                content=(
                    "What would you like me to do with that—recommend "
                    "something, find current information, explain it, or "
                    "help you play it?"
                ),
                success=True,
            )

        agent, capability = self._classify_task(
            message
        )

        project_scope = resolve_project_scope(
            message,
            payload,
        )

        history_items = (
            payload.get("history", [])
            if isinstance(
                payload.get("history"),
                list,
            )
            else []
        )

        follow_up_markers = (
            "what about",
            "how about",
            "how does that",
            "is there",
            "compare",
            "those",
            "them",
            "that one",
            "more detail",
            "continue",
            "still on",
            "regarding the first",
            "previous question",
        )

        is_follow_up = bool(
            history_items
            and any(
                marker in message.lower()
                for marker in follow_up_markers
            )
        )

        resolved_query = message

        if is_follow_up:
            recent_context = []

            for item in history_items[-8:]:
                if not isinstance(item, dict):
                    continue

                role = str(
                    item.get("role")
                    or item.get("type")
                    or ""
                ).lower()

                # Assistant output is continuity context, never factual
                # evidence and never part of a retrieval query.
                if role not in {"user", "human"}:
                    continue

                content = str(
                    item.get("content") or ""
                ).strip()

                if content:
                    recent_context.append(
                        content[:1200]
                    )

            if recent_context:
                resolved_query = (
                    "\n".join(recent_context)
                    + "\nCURRENT FOLLOW-UP: "
                    + message
                )

                contextual_agent, contextual_capability = (
                    self._classify_task(
                        resolved_query
                    )
                )

                if (
                    capability == "reasoning"
                    or any(
                        marker in message.lower()
                        for marker in follow_up_markers
                    )
                ):
                    agent = contextual_agent
                    capability = contextual_capability

        lowered_message = message.lower()
        context = await self._build_context(
            message,
            agent,
            payload.get("history", []),
            capability,
            project_scope.describe(),
        )

        context["resolved_query"] = resolved_query
        context["is_follow_up"] = is_follow_up

        if attachments:
            attachment_context = self.attachment_builder.build(
                query=message,
                attachments=attachments,
            )
            context["attachment_context"] = attachment_context

            event_bus = (
                getattr(self.system, "services", {}) or {}
            ).get("event_bus")

            if event_bus:
                event_bus.publish(
                    AIOSDomainEvent(
                        "attachment.context.created",
                        source="aios_dispatcher",
                        payload={
                            "attachment_count": attachment_context[
                                "attachment_count"
                            ],
                            "source_characters": attachment_context[
                                "source_characters"
                            ],
                            "context_characters": attachment_context[
                                "context_characters"
                            ],
                            "truncated": attachment_context["truncated"],
                        },
                    )
                )

        context.update(dispatch_context)

        request = CapabilityRequest(
            capability=capability,
            context=context,
        )

        result = await self.executor.execute(
            request
        )

        formatted = self._format_response(
            result,
            agent,
        )

        services = getattr(
            self.system,
            "services",
            {},
        ) or {}

        response_learning = services.get(
            "response_learning"
        )

        if response_learning is not None:
            try:
                learning_result = (
                    response_learning.capture(
                        request={
                            "message": message,
                            "project_id": project_scope.project_id,
                            "conversation_context":
                                context.get(
                                    "conversation_history",
                                    [],
                                ),
                        },
                        capability=capability,
                        agent=agent,
                        result=formatted,
                        evidence=(
                            result.get(
                                "execution_evidence",
                                {},
                            )
                            if isinstance(result, dict)
                            else {}
                        ),
                    )
                )

                formatted["learning"] = {
                    "record_id":
                        learning_result.get(
                            "record_id"
                        ),
                    "quality":
                        learning_result.get(
                            "evaluation",
                            {},
                        ).get(
                            "overall_score"
                        ),
                    "issues":
                        learning_result.get(
                            "evaluation",
                            {},
                        ).get(
                            "issues",
                            [],
                        ),
                }

            except Exception:
                logger.exception(
                    "AIOS response learning capture failed"
                )

        return formatted

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

        context.update(dispatch_context)

        request = CapabilityRequest(
            capability="reasoning",
            context = {
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

    @staticmethod
    def _needs_intent_clarification(message: str) -> bool:
        words = str(message or "").lower().split()

        if not words or len(words) > 10:
            return False

        subjective = {
            "real", "best", "good", "better", "proper", "actual",
        }
        explicit_actions = {
            "search", "find", "research", "recommend", "suggest", "play",
            "explain", "compare", "list", "news", "latest", "current",
            "where", "who", "what", "how", "why",
        }

        return bool(
            subjective.intersection(words)
            and not explicit_actions.intersection(words)
        )

    def _classify_task(
        self,
        message: str,
    ) -> Tuple[str, str]:

        text = message.lower()

        alpha_hunter_terms = (
            "undervalued", "underrated", "silent build", "silently building",
            "alpha hunter", "asymmetric opportunity", "investment opportunity",
            "tokenomics", "fully diluted valuation", "fdv", "token unlock",
            "vesting schedule", "treasury runway", "smart money",
            "venture due diligence", "startup due diligence",
        )
        if any(term in text for term in alpha_hunter_terms):
            return ("research", "research")

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
                "situation",
                "relations",
                "tensions",
                "conflict",
                "ceasefire",
                "sanctions",
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
        capability: str = "",
        project_scope: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        conversation_history = []

        if isinstance(history, list):
            for item in history[-10:]:
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
            "project_id": (
                project_scope or {}
            ).get("project_id", "aios-core"),
            "project_scope": project_scope or {},
        }

        services = getattr(
            self.system,
            "services",
            {},
        ) or {}

        # SuperContext runs only on the first conversational turn.
        # It is bounded, read-only, provider-independent, and optional.
        if not conversation_history:
            super_context = await self.super_context_builder.build(
                query=message,
                services=services,
            )

            if super_context.get("entries"):
                context["super_context"] = super_context

            super_context_event_bus = services.get("event_bus")

            if super_context_event_bus:
                super_context_event_bus.publish(
                    AIOSDomainEvent(
                        "context.super_context.prepared",
                        source="aios_dispatcher",
                        payload={
                            "agent": agent,
                            "status": super_context.get("status"),
                            "selected_count": super_context.get(
                                "selected_count",
                                0,
                            ),
                            "characters_used": super_context.get(
                                "characters_used",
                                0,
                            ),
                            "latency_ms": super_context.get(
                                "latency_ms",
                                0.0,
                            ),
                        },
                    )
                )

        response_learning = services.get(
            "response_learning"
        )

        if response_learning is not None:
            try:
                learned_lessons = response_learning.retrieve(
                    query=message,
                    capability=capability or agent,
                    limit=5,
                )

                if learned_lessons:
                    context["learned_lessons"] = (
                        learned_lessons
                    )

            except Exception:
                logger.exception(
                    "AIOS lesson retrieval failed"
                )

        mcp_registry = services.get("mcp_registry")
        mcp_client = services.get("mcp_client")

        tools = []
        skills = []
        capabilities = []
        agents = []

        if mcp_client and hasattr(mcp_client, "list_tools"):
            try:
                tools = await mcp_client.list_tools()
            except Exception:
                logger.exception("Compact context MCP discovery failed")

        if mcp_registry:
            try:
                context["mcp_servers"] = [
                    server.server_id
                    for server in await mcp_registry.get_all_servers()
                ]
            except Exception:
                context["mcp_servers"] = []

        skill_registry = services.get("skill_registry")

        if skill_registry:
            try:
                if hasattr(skill_registry, "list_skills"):
                    skills = skill_registry.list_skills()
                elif hasattr(skill_registry, "list"):
                    skills = skill_registry.list()
            except Exception:
                logger.exception("Compact context skill discovery failed")

        capability_registry = services.get("capability_registry")

        if capability_registry and hasattr(capability_registry, "list"):
            try:
                capabilities = capability_registry.list()
            except Exception:
                logger.exception("Compact context capability discovery failed")

        agent_manager = services.get("agent_manager")

        if agent_manager and hasattr(agent_manager, "describe"):
            try:
                agents = agent_manager.describe() or []
            except Exception:
                logger.exception("Compact context agent discovery failed")

        compact_context = self.context_builder.build(
            query=message,
            capability=agent,
            tools=tools,
            skills=skills,
            capabilities=capabilities,
            agents=agents,
        )

        context["compact_context"] = compact_context
        context["mcp_tools"] = [
            entry
            for entry in compact_context["entries"]
            if entry["kind"] == "tool"
        ]

        scoped_planner = services.get(
            "scoped_workflow_planner"
        )

        workflow_plan = None

        if scoped_planner:
            workflow_plan = scoped_planner.plan(
                query=message,
                category=agent,
                catalog=compact_context["entries"],
            )

        if workflow_plan:
            context["workflow_plan"] = workflow_plan

        event_bus = services.get("event_bus")

        if event_bus:
            event_bus.publish(
                AIOSDomainEvent(
                    "context.compacted",
                    source="aios_dispatcher",
                    payload={
                        "agent": agent,
                        "selected_count": compact_context["selected_count"],
                        "available_count": compact_context["available_count"],
                        "characters_used": compact_context["characters_used"],
                    },
                )
            )

            if workflow_plan:
                event_bus.publish(
                    AIOSDomainEvent(
                        "workflow.plan.created",
                        source="scoped_workflow_planner",
                        payload={
                            "plan_id": workflow_plan["plan_id"],
                            "category": workflow_plan["category"],
                            "mode": workflow_plan["mode"],
                            "status": workflow_plan["status"],
                            "step_count": len(workflow_plan["steps"]),
                            "council_required": workflow_plan[
                                "council_gate"
                            ]["required"],
                        },
                    )
                )

        diagnostic_patterns = (
            r"\baios\s+(?:status|health|runtime|telemetry|diagnostic)s?\b",
            r"\b(?:system|runtime)\s+(?:status|health|diagnostic)s?\b",
            r"\b(?:learning|event)\s+telemetry\b",
            r"\bprovider\s+(?:status|health|availability)\b",
            r"\bcouncil\s+(?:status|health|availability)\b",
            r"\bis\s+aios\s+(?:operational|healthy|online)\b",
        )

        if any(
            re.search(pattern, message.lower())
            for pattern in diagnostic_patterns
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
            "provider_cost": result.get(
                "provider_cost",
                0.0,
            ),
            "provider_latency": result.get(
                "provider_latency",
                0.0,
            ),
            "total_tokens": result.get(
                "total_tokens",
                0,
            ),
            "completion_tokens": result.get(
                "completion_tokens",
                0,
            ),
            "prompt_tokens": result.get(
                "prompt_tokens",
                0,
            ),
            "execution_evidence": result.get(
                "execution_evidence",
                {},
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
