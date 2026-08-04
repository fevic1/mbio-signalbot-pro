import logging

from aios.intelligence.capability_planner import CapabilityPlanner
from aios.intelligence.tool_executor import ToolExecutor

from aios.intelligence.evidence import (
    EvidenceCollection,
    DecisionEngine,
    EvidenceLearner,
    IntelligenceEngine,
    ReasoningEngine,
    IntelligencePlanner,
    IntelligenceRuntime,
    IntelligenceMemory,
    IntelligenceVerifier,
    IntelligenceGovernor,
    IntelligenceSnapshot,
    IntelligenceExecutor,
    IntelligenceAudit,
    IntelligenceOrchestrator,
    IntelligenceMetrics,
)

logger = logging.getLogger(__name__)


class ContextAssembler:

    async def assemble(
        self,
        system,
        capability,
        request,
    ):
        execution = getattr(
            request,
            "context",
            None,
        )

        if isinstance(execution, dict):
            metadata = dict(execution)
            results = dict(
                execution.get(
                    "results",
                    {},
                )
            )
        else:
            metadata = dict(
                getattr(
                    execution,
                    "metadata",
                    {},
                )
            ) if execution else {}

            results = dict(
                getattr(
                    execution,
                    "results",
                    {},
                )
            ) if execution else {}

        evidence = metadata.get("evidence")

        if evidence is None:
            evidence = EvidenceCollection()

        if isinstance(
            evidence,
            EvidenceCollection,
        ):
            evidence.normalize()

            report = evidence.intelligence_report()

            report["decision"] = (
                evidence.decision_context()
            )

            candidate = DecisionEngine().evaluate(
                evidence
            )

            report["candidate"] = {
                "action": candidate.action,
                "confidence": candidate.confidence,
                "rationale": candidate.rationale,
                "evidence": candidate.evidence,
                "constraints": candidate.constraints,
            }

            report["learning"] = (
                EvidenceLearner().learn(
                    evidence
                )
            )

            report["state"] = (
                IntelligenceEngine().build_state(
                    evidence
                )
            )

            report["reasoning"] = (
                ReasoningEngine().analyze(
                    evidence
                )
            )

            report["plan"] = (
                IntelligencePlanner().plan(
                    evidence
                )
            )

            runtime = IntelligenceRuntime().execute(
                evidence
            )

            report["runtime"] = runtime
            report["memory"] = (
                IntelligenceMemory().snapshot(
                    runtime
                )
            )

            report["verification"] = (
                IntelligenceVerifier().verify(
                    runtime
                )
            )

            report["governance"] = (
                IntelligenceGovernor().evaluate(
                    runtime
                )
            )

            report["snapshot"] = (
                IntelligenceSnapshot().build(
                    runtime
                )
            )

            execution = (
                IntelligenceExecutor().execute(
                    evidence
                )
            )

            report["execution"] = execution

            report["audit"] = (
                IntelligenceAudit().record(
                    execution
                )
            )

            orchestrator = (
                IntelligenceOrchestrator().run(
                    evidence
                )
            )

            report["orchestrator"] = orchestrator

            report["metrics"] = (
                IntelligenceMetrics().collect(
                    orchestrator
                )
            )
            report["coordinator"] = runtime["pipeline"]
            report["decision"] = runtime["decision"]
            report["reasoning"] = runtime["reasoning"]
            report["plan"] = runtime["plan"]
            report["learning"] = runtime["learning"]
            report["state"] = runtime["state"]
            report["explanation"] = runtime["explanation"]

            report["evidence"] = (
                evidence.as_prompt()
            )

            evidence_summary = report

        else:
            evidence_summary = {}


        capability_plan = []
        tool_results = []
        tool_evidence = {}

        registry = (
            system.get("mcp_registry")
            if hasattr(system, "get")
            else getattr(system, "mcp_registry", None)
        )

        if registry:

            try:

                capability_plan = await CapabilityPlanner().select(
                        registry,
                        getattr(
                            request,
                            "prompt",
                            getattr(
                                request,
                                "input",
                                "",
                            ),
                        ),
                    )

                if capability_plan:

                    execution = (
                        await ToolExecutor().execute(
                            registry,
                            capability_plan,
                        )
                    )

                    tool_results = execution.get(
                        "tool_results",
                        [],
                    )

                    tool_evidence = execution.get(
                        "tool_evidence",
                        {},
                    )

                    if isinstance(
                        evidence,
                        EvidenceCollection,
                    ):
                        merge_fn = getattr(evidence, "merge", None)
                        if callable(merge_fn):
                            merge_fn(tool_evidence)

                        evidence_summary = (
                            evidence.intelligence_report()
                        )

            except CapabilityExecutionError as exc:

                logger.warning(
                    "Capability planner unavailable; falling back to llm_only: %s",
                    exc,
                )

            except Exception:

                raise

        return {
            "capability": capability,
            "evidence": evidence,
            "evidence_summary": evidence_summary,
            "permission": request.permission,
            "retry_limit": request.retry_limit,
            "execution": execution,
            "results": results,
            "metadata": metadata,
            "memory": getattr(system, "memory", None),
            "project_manager": getattr(system, "project_manager", None),
            "event_bus": getattr(system, "event_bus", None),
            "decision_policy": getattr(system, "decision_policy", None),
            "skill_registry": getattr(system, "skill_registry", None),
            "capability_registry": getattr(system, "capability_registry", None),
            "capability_plan": capability_plan,
            "tool_results": tool_results,
            "tool_evidence": tool_evidence,
            "execution_mode": (
                "mcp_augmented"
                if tool_results
                else "llm_only"
            ),
            "tool_executor": ToolExecutor(),
        }
