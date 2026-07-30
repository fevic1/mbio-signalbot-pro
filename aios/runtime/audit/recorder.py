from pathlib import Path
import json

from .models import AuditEvent


class AuditRecorder:

    def __init__(self, root_dir=None):
        self.root = Path(
            root_dir or "."
        )

        self.path = (
            self.root
            / ".aios"
            / "audit"
        )

        self.path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.log_file = (
            self.path
            / "events.jsonl"
        )


    def record(
        self,
        event: AuditEvent,
    ):

        with self.log_file.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(
                    event.serialize()
                )
                + "\n"
            )

        return event


    def execution_event(
        self,
        task,
        policy_result,
        status,
    ):

        metadata = getattr(
            task,
            "metadata",
            {},
        )

        return self.record(
            AuditEvent(
                event_type="execution",
                timestamp=__import__(
                    "datetime"
                ).datetime.now(
                    __import__(
                        "datetime"
                    ).timezone.utc
                ).isoformat(),
                agent=metadata.get(
                    "agent_name",
                    "",
                ),
                task_id=getattr(
                    task,
                    "id",
                    "",
                ),
                prompt_hash=metadata.get(
                    "prompt_hash",
                    "",
                ),
                decision=str(
                    policy_result
                ),
                metadata={
                    "status": status,
                },
            )
        )
