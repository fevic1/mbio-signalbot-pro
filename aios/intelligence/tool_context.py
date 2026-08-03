from aios.intelligence.evidence import Evidence, EvidenceCollection
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


class ToolContextCompressor:
    """Compress large tool results while retaining recoverable originals."""

    def __init__(self):
        self.min_bytes = int(
            os.getenv("AIOS_TOOL_CONTEXT_MIN_BYTES", "2048")
        )
        self.max_entries = int(
            os.getenv("AIOS_TOOL_CONTEXT_MAX_ENTRIES", "256")
        )
        self.max_list_items = int(
            os.getenv("AIOS_TOOL_CONTEXT_MAX_LIST_ITEMS", "24")
        )
        self.store = Path(
            os.getenv(
                "AIOS_TOOL_CONTEXT_STORE",
                ".aios/context/tool_results",
            )
        )
        self.store.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _serialize(value: Any) -> str:
        if isinstance(value, str):
            return value

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    def _shrink(self, value: Any, depth: int = 0) -> Any:
        if depth >= 5:
            text = str(value)
            return text[:600] + ("…" if len(text) > 600 else "")

        if isinstance(value, dict):
            return {
                str(key): self._shrink(item, depth + 1)
                for key, item in value.items()
            }

        if isinstance(value, list):
            if len(value) <= self.max_list_items:
                return [
                    self._shrink(item, depth + 1)
                    for item in value
                ]

            head_count = max(1, self.max_list_items - 6)
            tail_count = min(4, len(value) - head_count)

            important = [
                item
                for item in value[head_count:-tail_count]
                if any(
                    term in str(item).lower()
                    for term in (
                        "error",
                        "failed",
                        "warning",
                        "exception",
                        "critical",
                    )
                )
            ][:2]

            return [
                *[
                    self._shrink(item, depth + 1)
                    for item in value[:head_count]
                ],
                {
                    "_aios_compacted": (
                        len(value)
                        - head_count
                        - tail_count
                    ),
                    "_important_middle_items": [
                        self._shrink(item, depth + 1)
                        for item in important
                    ],
                },
                *[
                    self._shrink(item, depth + 1)
                    for item in value[-tail_count:]
                ],
            ]

        if isinstance(value, str) and len(value) > 1600:
            return value[:1100] + "\n…\n" + value[-350:]

        return value

    @staticmethod
    def _compress_text(text: str) -> str:
        lines = text.splitlines()

        if len(lines) < 30:
            return text

        important = [
            line
            for line in lines
            if re.search(
                r"error|failed|warning|exception|traceback|critical",
                line,
                re.IGNORECASE,
            )
        ][:30]

        selected = [
            *lines[:12],
            *important,
            f"… {max(0, len(lines) - 24 - len(important))} lines omitted …",
            *lines[-12:],
        ]

        output = []
        seen = set()

        for line in selected:
            if line not in seen:
                output.append(line)
                seen.add(line)

        return "\n".join(output)

    def _prune(self) -> None:
        files = sorted(
            self.store.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

        for stale in files[self.max_entries:]:
            try:
                stale.unlink()
            except OSError:
                pass

    def prepare(self, tool_name: str, result: Any) -> Any:
        original = self._serialize(result)
        original_bytes = len(original.encode("utf-8"))

        if original_bytes < self.min_bytes:
            return result

        if isinstance(result, str):
            compact_value = self._compress_text(result)
        else:
            compact_value = self._shrink(result)

        compact = self._serialize(compact_value)

        if len(compact.encode("utf-8")) >= original_bytes * 0.85:
            return result

        digest = hashlib.sha256(
            original.encode("utf-8")
        ).hexdigest()

        record = {
            "token": digest,
            "tool": str(tool_name),
            "content": original,
            "original_bytes": original_bytes,
        }

        temporary = self.store / f".{digest}.tmp"
        destination = self.store / f"{digest}.json"

        temporary.write_text(
            json.dumps(
                record,
                ensure_ascii=False,
            )
        )
        temporary.replace(destination)
        self._prune()

        compact_bytes = len(compact.encode("utf-8"))

        return {
            "partial": True,
            "tool": str(tool_name),
            "content": compact_value,
            "retrieval_token": f"⟦aios-context:{digest}⟧",
            "original_bytes": original_bytes,
            "compact_bytes": compact_bytes,
            "bytes_saved": original_bytes - compact_bytes,
            "instruction": (
                "Use context__retrieve only if the omitted detail "
                "is required to answer accurately."
            ),
        }

    def retrieve(
        self,
        token: str,
        start_line: int = 1,
        end_line: int = 0,
    ) -> dict[str, Any]:
        match = re.fullmatch(
            r"(?:⟦aios-context:)?([a-f0-9]{64})(?:⟧)?",
            str(token).strip(),
        )

        if not match:
            return {
                "success": False,
                "error": "Invalid AIOS context token",
            }

        digest = match.group(1)
        source = self.store / f"{digest}.json"

        if not source.exists():
            return {
                "success": False,
                "error": "Context result not found or expired",
            }

        record = json.loads(source.read_text())
        content = str(record.get("content", ""))
        lines = content.splitlines()

        start = max(1, int(start_line or 1))
        end = int(end_line or 0)

        if end <= 0:
            end = len(lines)

        end = min(end, len(lines))

        if start > end and lines:
            return {
                "success": False,
                "error": "Invalid line range",
            }

        selected = "\n".join(lines[start - 1:end])

        return {
            "success": True,
            "token": digest,
            "tool": record.get("tool"),
            "start_line": start,
            "end_line": end,
            "total_lines": len(lines),
            "content": selected,
        }
