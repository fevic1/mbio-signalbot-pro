import re
from typing import Any


class AttachmentContextBuilder:
    """Build bounded, query-relevant excerpts from text attachments."""

    def __init__(
        self,
        max_context_chars: int = 60000,
        chunk_chars: int = 1800,
        overlap_chars: int = 200,
    ):
        self.max_context_chars = max_context_chars
        self.chunk_chars = chunk_chars
        self.overlap_chars = overlap_chars

    @staticmethod
    def _tokens(value: Any) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9_]+", str(value).lower())
            if len(token) > 1
        }

    def _chunks(self, content: str) -> list[dict[str, Any]]:
        chunks = []
        step = max(1, self.chunk_chars - self.overlap_chars)

        for start in range(0, len(content), step):
            text = content[start:start + self.chunk_chars]

            if not text:
                break

            chunks.append({
                "start": start,
                "end": start + len(text),
                "content": text,
            })

            if start + self.chunk_chars >= len(content):
                break

        return chunks

    def _score(self, query_tokens: set[str], text: str) -> float:
        if not query_tokens:
            return 0.0

        content_tokens = self._tokens(text)
        return len(query_tokens & content_tokens) / len(query_tokens)

    def build(
        self,
        query: str,
        attachments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        query_tokens = self._tokens(query)
        candidates = []

        for attachment_index, attachment in enumerate(attachments):
            content = str(attachment.get("content", ""))
            chunks = self._chunks(content)

            for chunk_index, chunk in enumerate(chunks):
                position_bonus = 0.0

                if chunk_index == 0:
                    position_bonus = 0.08
                elif chunk_index == len(chunks) - 1:
                    position_bonus = 0.04

                candidates.append({
                    "attachment_index": attachment_index,
                    "attachment_id": attachment.get("id"),
                    "name": attachment.get("name", "Pasted text"),
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "content": chunk["content"],
                    "score": (
                        self._score(query_tokens, chunk["content"])
                        + position_bonus
                    ),
                })

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        selected = []
        used_chars = 0
        seen = set()

        for candidate in candidates:
            key = (
                candidate["attachment_index"],
                candidate["start"],
            )

            if key in seen:
                continue

            size = len(candidate["content"])

            if used_chars + size > self.max_context_chars:
                continue

            selected.append(candidate)
            seen.add(key)
            used_chars += size

            if used_chars >= self.max_context_chars:
                break

        selected.sort(
            key=lambda item: (
                item["attachment_index"],
                item["start"],
            )
        )

        return {
            "attachment_count": len(attachments),
            "source_characters": sum(
                len(str(item.get("content", "")))
                for item in attachments
            ),
            "context_characters": used_chars,
            "truncated": used_chars < sum(
                len(str(item.get("content", "")))
                for item in attachments
            ),
            "attachments": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": item.get("type", "text/plain"),
                    "characters": len(str(item.get("content", ""))),
                    "lines": str(item.get("content", "")).count("\n") + 1,
                }
                for item in attachments
            ],
            "excerpts": selected,
        }
