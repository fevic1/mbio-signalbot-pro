from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Evidence:

    source: str
    category: str
    claim: str

    confidence: float = 1.0
    verified: bool = False

    url: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class EvidenceCollection:

    def __init__(self):

        self._items: list[Evidence] = []

    def add(self, evidence: Evidence):

        self._items.append(evidence)

    def extend(self, items):

        for item in items:
            self.add(item)

    def all(self):

        return list(self._items)

    def verified(self):

        return [
            e for e in self._items
            if e.verified
        ]

    def by_category(self, category):

        return [
            e for e in self._items
            if e.category == category
        ]

    def confidence(self):

        if not self._items:
            return 0.0

        return (
            sum(e.confidence for e in self._items)
            / len(self._items)
        )

    def as_prompt(self):

        return [
            {
                "source": e.source,
                "category": e.category,
                "claim": e.claim,
                "confidence": e.confidence,
                "verified": e.verified,
                "url": e.url,
                "timestamp": e.timestamp,
                "metadata": e.metadata,
            }
            for e in self._items
        ]


    def normalize(self):

        unique = {}

        for item in self._items:

            key = (
                item.category,
                item.claim.strip().lower(),
            )

            current = unique.get(key)

            if (
                current is None
                or item.confidence > current.confidence
            ):
                unique[key] = item

        self._items = sorted(
            unique.values(),
            key=lambda e: (
                e.verified,
                e.confidence,
                e.timestamp,
            ),
            reverse=True,
        )

        return self


    def conflicts(self):

        conflicts = {}

        for item in self._items:

            key = (
                item.category,
                item.source,
            )

            conflicts.setdefault(
                key,
                set(),
            ).add(
                item.claim.strip()
            )

        return {
            str(k): sorted(v)
            for k, v in conflicts.items()
            if len(v) > 1
        }


    def summary(self):

        self.normalize()

        return {
            "count": len(self._items),
            "verified": len(
                self.verified()
            ),
            "confidence": self.confidence(),
            "conflicts": self.conflicts(),
            "categories": sorted(
                {
                    e.category
                    for e in self._items
                }
            ),
        }


    def ranked(self):

        self.normalize()

        return sorted(
            self._items,
            key=lambda e: (
                e.verified,
                e.confidence,
                e.freshness,
            ),
            reverse=True,
        )


    def top(
        self,
        limit=10,
    ):

        return self.ranked()[:limit]


    def consensus(self):

        self.normalize()

        total = len(self._items)

        if total == 0:
            return {
                "score": 0.0,
                "agreement": 0,
                "conflicts": 0,
            }

        conflicts = self.conflicts()

        agreement = total - len(conflicts)

        score = round(
            agreement / total,
            3,
        )

        return {
            "score": score,
            "agreement": agreement,
            "conflicts": len(conflicts),
        }


    def confidence_breakdown(self):

        return {
            "overall": self.confidence(),
            "consensus": self.consensus(),
            "verified": len(self.verified()),
            "sources": sorted(
                {
                    e.source
                    for e in self._items
                }
            ),
        }


    def source_rankings(self):

        rankings = {}

        for item in self._items:

            entry = rankings.setdefault(
                item.source,
                {
                    "count": 0,
                    "confidence": [],
                    "verified": 0,
                },
            )

            entry["count"] += 1
            entry["confidence"].append(item.confidence)

            if item.verified:
                entry["verified"] += 1

        for source, entry in rankings.items():

            scores = entry.pop("confidence")

            entry["average_confidence"] = round(
                sum(scores) / len(scores),
                3,
            )

        return dict(
            sorted(
                rankings.items(),
                key=lambda kv: (
                    kv[1]["average_confidence"],
                    kv[1]["verified"],
                    kv[1]["count"],
                ),
                reverse=True,
            )
        )


    def intelligence_report(self):

        return {
            "summary": self.summary(),
            "confidence": self.confidence_breakdown(),
            "sources": self.source_rankings(),
            "top": [
                vars(item)
                for item in self.top(10)
            ],
        }


    def decision_context(self):

        report = self.intelligence_report()

        return {
            "confidence": report["confidence"],
            "sources": report["sources"],
            "summary": report["summary"],
            "top_evidence": report["top"],
            "recommended_sources": [
                source
                for source in report["sources"]
            ][:5],
            "overall_confidence": report["confidence"]["overall"],
            "consensus_score": report["confidence"]["consensus"]["score"],
        }


from dataclasses import dataclass


@dataclass(slots=True)
class DecisionCandidate:

    action: str
    confidence: float
    rationale: str
    evidence: list
    constraints: list


class DecisionEngine:

    def evaluate(
        self,
        evidence,
    ):

        ctx = evidence.decision_context()

        confidence = ctx["overall_confidence"]

        if confidence >= 0.90:
            level = "high"

        elif confidence >= 0.70:
            level = "medium"

        else:
            level = "low"

        return DecisionCandidate(
            action="reason",
            confidence=confidence,
            rationale=f"{level} evidence confidence",
            evidence=ctx["top_evidence"],
            constraints=[
                "verify_conflicts",
                "respect_risk_policy",
            ],
        )


from dataclasses import dataclass


@dataclass(slots=True)
class LearningSignal:

    source: str
    confidence: float
    successful: bool
    verified: bool


class EvidenceLearner:

    def learn(self, evidence):

        report = evidence.intelligence_report()

        signals = []

        for item in evidence.top(100):

            signals.append(
                LearningSignal(
                    source=item.source,
                    confidence=item.confidence,
                    successful=item.verified,
                    verified=item.verified,
                )
            )

        return {
            "signals": [
                {
                    "source": s.source,
                    "confidence": s.confidence,
                    "successful": s.successful,
                    "verified": s.verified,
                }
                for s in signals
            ],
            "sources": report["sources"],
            "confidence": report["confidence"],
        }


from dataclasses import dataclass, field


@dataclass(slots=True)
class IntelligenceState:

    evidence_count: int = 0
    verified_count: int = 0
    confidence: float = 0.0
    consensus: float = 0.0
    sources: dict = field(default_factory=dict)
    learning: dict = field(default_factory=dict)


class IntelligenceEngine:

    def build_state(
        self,
        evidence,
    ):

        report = evidence.intelligence_report()

        state = IntelligenceState(
            evidence_count=report["summary"]["count"],
            verified_count=report["confidence"]["verified"],
            confidence=report["confidence"]["overall"],
            consensus=report["confidence"]["consensus"]["score"],
            sources=report["sources"],
            learning=EvidenceLearner().learn(
                evidence
            ),
        )

        return {
            "evidence_count": state.evidence_count,
            "verified_count": state.verified_count,
            "confidence": state.confidence,
            "consensus": state.consensus,
            "sources": state.sources,
            "learning": state.learning,
        }


class ReasoningEngine:

    def analyze(
        self,
        evidence,
    ):

        state = IntelligenceEngine().build_state(
            evidence
        )

        decision = DecisionEngine().evaluate(
            evidence
        )

        return {
            "confidence": state["confidence"],
            "consensus": state["consensus"],
            "decision": {
                "action": decision.action,
                "confidence": decision.confidence,
                "rationale": decision.rationale,
            },
            "learning": state["learning"],
            "sources": state["sources"],
        }


class IntelligencePlanner:

    def plan(
        self,
        evidence,
    ):

        reasoning = ReasoningEngine().analyze(
            evidence
        )

        decision = reasoning["decision"]

        return {
            "goal": decision["action"],
            "priority": (
                "high"
                if decision["confidence"] >= 0.90
                else "medium"
                if decision["confidence"] >= 0.70
                else "low"
            ),
            "confidence": decision["confidence"],
            "steps": [
                "collect_evidence",
                "verify_sources",
                "evaluate_consensus",
                "generate_decision",
            ],
        }


class ExplanationEngine:

    def explain(
        self,
        evidence,
    ):

        planner = IntelligencePlanner().plan(
            evidence
        )

        state = IntelligenceEngine().build_state(
            evidence
        )

        return {
            "summary":
                f"{state['verified_count']} verified evidence "
                f"from {len(state['sources'])} sources.",
            "planner": planner,
            "confidence": state["confidence"],
            "consensus": state["consensus"],
        }


class IntelligenceCoordinator:

    def execute(
        self,
        evidence,
    ):

        return {
            "state": IntelligenceEngine().build_state(
                evidence
            ),
            "reasoning": ReasoningEngine().analyze(
                evidence
            ),
            "plan": IntelligencePlanner().plan(
                evidence
            ),
            "decision": DecisionEngine().evaluate(
                evidence
            ),
            "learning": EvidenceLearner().learn(
                evidence
            ),
            "explanation": ExplanationEngine().explain(
                evidence
            ),
        }


class IntelligenceRuntime:

    def execute(
        self,
        evidence,
    ):

        coordinator = IntelligenceCoordinator().execute(
            evidence
        )

        return {
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").UTC
            ).isoformat(),
            "pipeline": coordinator,
            "decision": coordinator["decision"],
            "reasoning": coordinator["reasoning"],
            "plan": coordinator["plan"],
            "learning": coordinator["learning"],
            "state": coordinator["state"],
            "explanation": coordinator["explanation"],
        }


class IntelligenceMemory:

    def snapshot(
        self,
        runtime,
    ):

        pipeline = runtime["pipeline"]

        return {
            "timestamp": runtime["timestamp"],
            "confidence": runtime["state"]["confidence"],
            "consensus": runtime["state"]["consensus"],
            "verified": runtime["state"]["verified_count"],
            "sources": runtime["state"]["sources"],
            "decision": {
                "action": pipeline["decision"].action,
                "confidence": pipeline["decision"].confidence,
                "rationale": pipeline["decision"].rationale,
            },
            "learning": runtime["learning"],
        }


class IntelligenceVerifier:

    def verify(
        self,
        runtime,
    ):

        state = runtime["state"]

        passed = (
            state["confidence"] >= 0.70
            and state["consensus"] >= 0.60
        )

        return {
            "passed": passed,
            "confidence": state["confidence"],
            "consensus": state["consensus"],
            "verified": state["verified_count"],
            "reasons": (
                []
                if passed
                else [
                    "low_confidence",
                    "low_consensus",
                ]
            ),
        }


class IntelligenceGovernor:

    def evaluate(
        self,
        runtime,
    ):

        verification = IntelligenceVerifier().verify(
            runtime
        )

        decision = runtime["decision"]

        return {
            "approved": verification["passed"],
            "blocked": not verification["passed"],
            "decision": {
                "action": decision.action,
                "confidence": decision.confidence,
                "rationale": decision.rationale,
            },
            "verification": verification,
        }


class IntelligenceSnapshot:

    def build(
        self,
        runtime,
    ):

        governor = IntelligenceGovernor().evaluate(
            runtime
        )

        return {
            "timestamp": runtime["timestamp"],
            "state": runtime["state"],
            "reasoning": runtime["reasoning"],
            "plan": runtime["plan"],
            "learning": runtime["learning"],
            "memory": IntelligenceMemory().snapshot(
                runtime
            ),
            "verification": governor["verification"],
            "governance": governor,
        }
