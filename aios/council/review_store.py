import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import uuid
from urllib.parse import urlparse

from aios.events.models import AIOSDomainEvent


class CouncilReviewStore:
    """Persistent Council discussions and human decisions."""

    FINAL_STATES = {
        "approved",
        "rejected",
        "changes_requested",
    }

    def __init__(
        self,
        path="/app/data/aios/council_reviews.json",
        event_bus=None,
        approval_manager=None,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.event_bus = event_bus
        self.approval_manager = approval_manager

        if not self.path.exists():
            self._write([])

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def _load(self):
        try:
            data = json.loads(self.path.read_text())
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, records):
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(
                records,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )
        temporary.replace(self.path)

    def _emit(self, event_type, review):
        if self.event_bus:
            self.event_bus.publish(
                AIOSDomainEvent(
                    event_type,
                    source="council_review_store",
                    payload={
                        "review_id": review["id"],
                        "status": review["status"],
                        "severity": review["severity"],
                        "title": review["title"],
                    },
                )
            )

    def create(
        self,
        title,
        description,
        severity="medium",
        source="aios",
        evidence=None,
        session=None,
    ):
        records = self._load()

        fingerprint = hashlib.sha256(
            f"{source}|{title}|{description}"
            .lower()
            .encode("utf-8")
        ).hexdigest()

        for record in records:
            if (
                record.get("fingerprint") == fingerprint
                and record.get("status") not in self.FINAL_STATES
            ):
                record["occurrences"] = (
                    record.get("occurrences", 1) + 1
                )
                record["updated_at"] = self._now()
                record["unread"] = True
                self._write(records)
                self._emit("council.review.updated", record)
                return record

        review_id = str(uuid.uuid4())
        approval_id = None

        if self.approval_manager:
            approval = self.approval_manager.create_request(
                action=f"Council review: {title}",
                requested_by="council",
                payload={
                    "review_id": review_id,
                    "severity": severity,
                    "source": source,
                },
            )
            approval_id = approval["id"]

        now = self._now()

        review = {
            "id": review_id,
            "fingerprint": fingerprint,
            "title": str(title),
            "description": str(description),
            "severity": str(severity).lower(),
            "source": str(source),
            "status": "awaiting_human",
            "agent_states": {
                "architect": "waiting",
                "risk": "waiting",
                "skeptic": "waiting",
                "verification": "waiting",
                "chair": "waiting",
            },
            "approval_id": approval_id,
            "evidence": evidence or [],
            "session": session,
            "discussion": [],
            "synthesis": None,
            "human_decision": None,
            "human_actor": None,
            "human_reason": None,
            "occurrences": 1,
            "unread": True,
            "created_at": now,
            "updated_at": now,
        }

        records.append(review)
        self._write(records)
        self._emit("council.review.created", review)
        return review

    def all(self):
        return sorted(
            [self._present_record(item) for item in self._load()],
            key=lambda item: item.get("updated_at", ""),
            reverse=True,
        )

    def get(self, review_id):
        return next(
            (
                self._present_record(record)
                for record in self._load()
                if record.get("id") == review_id
            ),
            None,
        )

    def _present_record(self, record):
        """Keep raw audit evidence while presenting legacy faults clearly."""
        result = dict(record)
        if not str(result.get("title", "")).startswith("AIOS fault:"):
            return result

        evidence = result.get("evidence") or []
        event = evidence[0] if evidence and isinstance(evidence[0], dict) else {}
        payload = event.get("payload") or {}
        message = (
            payload.get("error")
            or payload.get("message")
            or result.get("description", "")
        )
        title, description = self._fault_summary(
            event.get("event_type") or str(result.get("title", "")).split(":", 1)[-1].strip(),
            payload,
            str(message),
        )
        result["title"] = title
        result["description"] = description
        return result

    def pending(self):
        return [
            record
            for record in self.all()
            if record.get("status") == "awaiting_human"
        ]

    def unread_count(self):
        return sum(
            1 for record in self._load()
            if record.get("unread")
        )

    def add_message(
        self,
        review_id,
        actor,
        message,
        role="human",
        target="all",
        confidence=None,
        evidence=None,
    ):
        records = self._load()

        for record in records:
            if record.get("id") != review_id:
                continue

            record.setdefault("discussion", []).append({
                "id": str(uuid.uuid4()),
                "actor": str(actor),
                "role": str(role),
                "target": str(target),
                "message": str(message),
                "confidence": confidence,
                "evidence": evidence or [],
                "timestamp": self._now(),
            })

            if role == "agent" and actor in record["agent_states"]:
                record["agent_states"][actor] = "responded"

            record["updated_at"] = self._now()
            record["unread"] = role != "human"

            self._write(records)
            self._emit("council.discussion.added", record)
            return record

        return None

    def set_agent_state(
        self,
        review_id,
        agent,
        state,
    ):
        records = self._load()

        for record in records:
            if record.get("id") != review_id:
                continue

            record.setdefault(
                "agent_states",
                {},
            )[str(agent)] = str(state)

            record["updated_at"] = self._now()
            self._write(records)
            return record

        return None

    def set_synthesis(
        self,
        review_id,
        summary,
        agreements=None,
        disagreements=None,
        risks=None,
        recommendation=None,
    ):
        records = self._load()

        for record in records:
            if record.get("id") != review_id:
                continue

            record["synthesis"] = {
                "summary": str(summary),
                "agreements": agreements or [],
                "disagreements": disagreements or [],
                "risks": risks or [],
                "recommendation": recommendation,
                "created_at": self._now(),
            }
            record["agent_states"]["chair"] = "responded"
            record["updated_at"] = self._now()
            record["unread"] = True

            self._write(records)
            self._emit("council.synthesis.created", record)
            return record

        return None

    def decide(
        self,
        review_id,
        decision,
        actor="human",
        reason="",
    ):
        if decision not in self.FINAL_STATES:
            raise ValueError("Invalid human decision")

        records = self._load()

        for record in records:
            if record.get("id") != review_id:
                continue

            if record.get("human_decision"):
                raise ValueError(
                    "Review already has a human decision"
                )

            approval_id = record.get("approval_id")

            if self.approval_manager and approval_id:
                if decision == "approved":
                    self.approval_manager.approve(
                        approval_id,
                        actor,
                    )
                else:
                    self.approval_manager.reject(
                        approval_id,
                        actor,
                    )

            record["status"] = decision
            record["human_decision"] = decision
            record["human_actor"] = str(actor)
            record["human_reason"] = str(reason)
            record["decided_at"] = self._now()
            record["updated_at"] = self._now()
            record["unread"] = False

            self._write(records)
            self._emit(
                f"council.review.{decision}",
                record,
            )
            return record

        return None

    def mark_read(self, review_id):
        records = self._load()

        for record in records:
            if record.get("id") == review_id:
                record["unread"] = False
                record["updated_at"] = self._now()
                self._write(records)
                return record

        return None

    def capture_event(self, event):
        event_type = getattr(event, "event_type", "")

        relevant = (
            event_type.endswith(".failed")
            or event_type.endswith(".error")
            or event_type in {
                "system.fault",
                "runtime.failure",
                "governance.violation",
            }
        )

        if not relevant:
            return None

        payload = getattr(event, "payload", {}) or {}
        message = (
            payload.get("error")
            or payload.get("message")
            or payload.get("reason")
            or event_type
        )

        title, description = self._fault_summary(
            event_type,
            payload,
            str(message),
        )

        return self.create(
            title=title,
            description=description,
            severity=payload.get("severity", "high"),
            source=getattr(event, "source", "event_bus"),
            evidence=[{
                "event_id": getattr(event, "id", None),
                "event_type": event_type,
                "payload": payload,
                "timestamp": getattr(event, "timestamp", None),
            }],
        )

    @staticmethod
    def _fault_summary(event_type, payload, message):
        """Convert internal exceptions into decision-ready Council language."""
        lowered = message.lower()
        provider = str(
            payload.get("provider")
            or payload.get("source")
            or "model provider"
        ).strip()

        if "429" in lowered or "too many requests" in lowered:
            host = ""
            for token in message.replace("'", " ").split():
                if token.startswith(("http://", "https://")):
                    host = urlparse(token).netloc
                    break

            if host and provider == "model provider":
                provider = host.split(".")[1] if "." in host else host

            display = provider.replace("_", " ").strip().title()
            return (
                f"{display} request limit reached",
                f"{display} temporarily rejected a model request because its "
                "rate limit was reached. AIOS should fail over to another "
                "healthy provider and retry after the cooldown; no user or "
                "project action was executed.",
            )

        if event_type == "provider_execution.failed":
            display = provider.replace("_", " ").strip().title()
            return (
                f"{display} model request failed",
                f"A request to {display} did not complete. AIOS should verify "
                "provider health, use the configured fallback path, and retain "
                "the original error only as technical evidence.",
            )

        clean_type = event_type.replace(".", " ").replace("_", " ")
        return (
            clean_type.title(),
            "AIOS detected an operational fault that requires review. The "
            "technical payload is retained as evidence; no corrective action "
            "has been executed without approval.",
        )
