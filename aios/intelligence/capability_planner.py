
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(slots=True)
class CapabilityCandidate:
    server: str
    tool: str
    score: float


class CapabilityPlanner:

    def plan(
        self,
        registry,
        request: str,
    ):

        request = request.lower()

        candidates = []

        for server, tools in getattr(
            registry,
            "_tools",
            {},
        ).items():

            for tool in tools:

                score = max(
                    SequenceMatcher(
                        None,
                        request,
                        tool.lower(),
                    ).ratio(),
                    SequenceMatcher(
                        None,
                        request,
                        server.lower(),
                    ).ratio(),
                )

                keywords = (
                    tool
                    + " "
                    + server
                ).lower()

                for token in request.split():

                    if token in keywords:
                        score += 0.15

                candidates.append(
                    CapabilityCandidate(
                        server,
                        tool,
                        round(score,3),
                    )
                )

        candidates.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return candidates

    def select(
        self,
        registry,
        request,
        limit=5,
    ):
        return self.plan(
            registry,
            request,
        )[:limit]
