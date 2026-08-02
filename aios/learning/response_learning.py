import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from aios.memory.models import (
    MemoryImportance,
    MemoryMetadata,
    MemoryRecord,
    MemoryType,
)


URL_PATTERN = re.compile(r"https?://[^\s)\]}>\"']+")


class ResponseQualityEvaluator:
    """Deterministic first-pass evaluation of an AIOS response."""

    def evaluate(
        self,
        request: Dict[str, Any],
        result: Dict[str, Any],
        evidence: Dict[str, Any],
    ) -> Dict[str, Any]:

        message = str(request.get("message") or "")
        content = str(result.get("content") or "")
        lowered = message.lower()

        research = evidence.get("research_context") or {}
        sources = research.get("results") or []

        cited_urls = {
            url.rstrip(".,;:")
            for url in URL_PATTERN.findall(content)
        }

        exact_urls = {
            str(source.get("url") or "").strip()
            for source in sources
            if source.get("url")
        }

        verified_urls = {
            str(source.get("url") or "").strip()
            for source in sources
            if source.get("url")
            and source.get("verified_by") == "firecrawl"
        }

        external_request = any(
            term in lowered
            for term in (
                "search",
                "latest",
                "current",
                "today",
                "news",
                "research",
                "look up",
                "find online",
                "source",
                "cite",
            )
        )

        requested_count = None
        count_match = re.search(
            r"\b(?:give|list|provide)\s+(\d+)\b",
            lowered,
        )
        if count_match:
            requested_count = int(count_match.group(1))

        bullet_count = len(
            re.findall(r"(?m)^\s*(?:[-*]|\d+[.)])\s+", content)
        )

        issues: List[str] = []

        if not content.strip():
            issues.append("empty_response")

        if external_request and not sources:
            issues.append("missing_external_evidence")

        if sources and len(verified_urls) < len(exact_urls):
            issues.append("unverified_sources_present")

        if verified_urls and not verified_urls.issubset(cited_urls):
            issues.append("missing_exact_verified_citations")

        if external_request and not cited_urls:
            issues.append("missing_citations")

        if (
            "verified research" in content.lower()
            and sources
            and len(verified_urls) < len(exact_urls)
        ):
            issues.append("unsupported_verified_label")

        if requested_count is not None and bullet_count < requested_count:
            issues.append("incomplete_requested_items")

        if evidence.get("fallback_used"):
            issues.append("fallback_used")

        if external_request:
            grounding = (
                len(verified_urls) / max(len(exact_urls), 1)
            )
            citation_validity = (
                len(verified_urls.intersection(cited_urls))
                / max(len(verified_urls), 1)
                if verified_urls
                else 0.0
            )
        else:
            grounding = 1.0
            citation_validity = 1.0

        completeness = 1.0
        if not content.strip():
            completeness = 0.0
        elif requested_count is not None:
            completeness = min(
                bullet_count / max(requested_count, 1),
                1.0,
            )

        success = bool(result.get("success", True))
        reliability = 1.0 if success else 0.0

        overall = round(
            (
                grounding * 0.35
                + citation_validity * 0.25
                + completeness * 0.25
                + reliability * 0.15
            ),
            4,
        )

        return {
            "overall_score": overall,
            "citation_validity": round(citation_validity, 4),
            "factual_grounding": round(grounding, 4),
            "completeness": round(completeness, 4),
            "reliability": reliability,
            "issues": issues,
            "source_count": len(exact_urls),
            "verified_source_count": len(verified_urls),
            "cited_url_count": len(cited_urls),
        }


class ResponseLearningEngine:
    """Immediate response learning using the native AIOS memory router."""

    LESSON_ACTIONS = {
        "missing_external_evidence": (
            "Do not answer time-sensitive research requests without "
            "retrieved evidence; disclose that evidence is unavailable."
        ),
        "unverified_sources_present": (
            "Treat Tavily snippets as discovery evidence only. Do not "
            "describe a claim as verified until the source is inspected."
        ),
        "missing_exact_verified_citations": (
            "Cite the exact inspected article URL beside every factual claim."
        ),
        "missing_citations": (
            "For external research, include exact source URLs in the answer."
        ),
        "unsupported_verified_label": (
            "Never label research as verified when any supporting source "
            "was not successfully inspected."
        ),
        "incomplete_requested_items": (
            "Return every item explicitly requested by the user and verify "
            "the requested count before responding."
        ),
        "fallback_used": (
            "Disclose provider or tool fallback and reduce certainty when "
            "the preferred evidence path fails."
        ),
        "empty_response": (
            "Return a useful failure explanation when generation produces "
            "no response content."
        ),
    }

    def __init__(self, memory_manager, event_bus=None):
        self.memory = memory_manager
        self.event_bus = event_bus
        self.evaluator = ResponseQualityEvaluator()

    def _publish(self, event_type, payload):
        if self.event_bus is None:
            return

        try:
            from aios.events import AIOSDomainEvent

            self.event_bus.publish(
                AIOSDomainEvent(
                    event_type=event_type,
                    source="response_learning",
                    payload=payload,
                )
            )
        except Exception:
            # Learning must not interrupt a user response.
            return

    def _records(self, memory_type):
        records = self.memory.retrieve(memory_type)
        return records if isinstance(records, list) else []

    def _lesson_fingerprint(self, capability, issue, action):
        value = f"{capability}|{issue}|{action}"
        return hashlib.sha256(value.encode()).hexdigest()

    def capture(
        self,
        request,
        capability,
        agent,
        result,
        evidence=None,
    ):
        evidence = evidence or {}

        evaluation = self.evaluator.evaluate(
            request=request,
            result=result,
            evidence=evidence,
        )

        record_content = {
            "record_kind": "response_execution",
            "request": {
                "message": str(request.get("message") or "")[:12000],
                "conversation_context": list(
                    request.get("conversation_context") or []
                )[-12:],
            },
            "capability": capability,
            "agent": agent,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "tools_called": list(
                evidence.get("tools_called") or []
            ),
            "sources": list(
                (evidence.get("research_context") or {}).get(
                    "results", []
                )
            )[:12],
            "final_response": str(
                result.get("content") or ""
            )[:30000],
            "evaluation": evaluation,
            "latency": result.get("latency"),
            "attempt": result.get("attempt"),
            "fallback_used": bool(
                evidence.get("fallback_used")
            ),
            "user_feedback": None,
            "recorded_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        response_record = MemoryRecord(
            content=record_content,
            memory_type=MemoryType.FEEDBACK,
            importance=(
                MemoryImportance.HIGH
                if evaluation["overall_score"] < 0.6
                else MemoryImportance.NORMAL
            ),
            metadata=MemoryMetadata(
                source="response_learning",
                tags=[
                    "response_execution",
                    f"capability:{capability}",
                    f"agent:{agent}",
                ],
                confidence=evaluation["overall_score"],
            ),
        )

        stored_record = self.memory.store(response_record)

        lessons = []
        for issue in evaluation["issues"]:
            action = self.LESSON_ACTIONS.get(issue)
            if not action:
                continue

            fingerprint = self._lesson_fingerprint(
                capability,
                issue,
                action,
            )

            previous = [
                item
                for item in self._records(MemoryType.KNOWLEDGE)
                if item.content.get("record_kind") == "response_lesson"
                and item.content.get("fingerprint") == fingerprint
            ]

            occurrence = len(previous) + 1
            confidence = min(0.55 + occurrence * 0.1, 0.99)

            lesson = {
                "record_kind": "response_lesson",
                "fingerprint": fingerprint,
                "capability": capability,
                "trigger": issue,
                "lesson": action,
                "action": action,
                "occurrences": occurrence,
                "confidence": confidence,
                "evidence_record_id": response_record.id,
                "status": "active",
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            lesson_record = MemoryRecord(
                content=lesson,
                memory_type=MemoryType.KNOWLEDGE,
                importance=(
                    MemoryImportance.HIGH
                    if occurrence >= 3
                    else MemoryImportance.NORMAL
                ),
                metadata=MemoryMetadata(
                    source="response_learning",
                    tags=[
                        "response_lesson",
                        f"capability:{capability}",
                        f"trigger:{issue}",
                    ],
                    confidence=confidence,
                ),
            )

            self.memory.store(lesson_record)
            lessons.append(lesson)

        self._publish(
            "learning.response.evaluated",
            {
                "record_id": response_record.id,
                "capability": capability,
                "score": evaluation["overall_score"],
                "issues": evaluation["issues"],
                "lessons_created": len(lessons),
            },
        )

        return {
            "record_id": response_record.id,
            "stored": stored_record is not None,
            "evaluation": evaluation,
            "lessons": lessons,
        }

    def retrieve(self, query, capability, limit=5):
        query_terms = {
            term
            for term in re.findall(
                r"[a-z0-9_]{3,}",
                str(query).lower(),
            )
        }

        grouped = {}

        for record in self._records(MemoryType.KNOWLEDGE):
            lesson = record.content

            if lesson.get("record_kind") != "response_lesson":
                continue
            if lesson.get("status") != "active":
                continue

            fingerprint = lesson.get("fingerprint")
            current = grouped.get(fingerprint)

            if (
                current is None
                or lesson.get("occurrences", 0)
                > current.get("occurrences", 0)
            ):
                grouped[fingerprint] = lesson

        ranked = []

        for lesson in grouped.values():
            text = " ".join(
                str(lesson.get(key) or "")
                for key in ("trigger", "lesson", "action")
            ).lower()

            lesson_terms = set(
                re.findall(r"[a-z0-9_]{3,}", text)
            )

            overlap = len(query_terms.intersection(lesson_terms))
            capability_match = (
                4 if lesson.get("capability") == capability else 0
            )

            score = (
                capability_match
                + overlap
                + float(lesson.get("confidence", 0))
                + min(int(lesson.get("occurrences", 1)), 5) * 0.2
            )

            if capability_match or overlap:
                ranked.append((score, lesson))

        selected = [
            lesson
            for _, lesson in sorted(
                ranked,
                key=lambda item: item[0],
                reverse=True,
            )[:limit]
        ]

        self._publish(
            "learning.lessons.retrieved",
            {
                "capability": capability,
                "count": len(selected),
                "fingerprints": [
                    lesson.get("fingerprint")
                    for lesson in selected
                ],
            },
        )

        return selected
