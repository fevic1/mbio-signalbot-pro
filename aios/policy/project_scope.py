"""Project isolation policy for AIOS requests and delegated tools."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectScope:
    project_id: str
    owner: str
    role: str
    allowed_servers: tuple[str, ...]
    delegated_execution_servers: tuple[str, ...] = ()
    direct_trading_execution: bool = False

    def describe(self) -> dict[str, Any]:
        return asdict(self)


AIOS_CORE = ProjectScope(
    project_id="aios-core",
    owner="aios",
    role="operating_system",
    allowed_servers=("internet", "ipinfo", "tavily", "firecrawl"),
)

MBIO_SIGNALPRO = ProjectScope(
    project_id="mbio-signalpro",
    owner="mbio-signalpro",
    role="managed_application",
    allowed_servers=(
        "internet",
        "ipinfo",
        "tavily",
        "firecrawl",
        "risk-analyzer",
    ),
    delegated_execution_servers=("vibe-trading",),
    direct_trading_execution=False,
)


def resolve_project_scope(
    message: str,
    payload: dict[str, Any] | None = None,
) -> ProjectScope:
    """Resolve scope explicitly; generic crypto language never implies MBIO."""

    payload = payload or {}
    requested = str(
        payload.get("project_id")
        or payload.get("project")
        or ""
    ).strip().lower()
    lowered = message.lower()

    if requested in {"mbio", "mbio-signalpro", "signalpro"}:
        return MBIO_SIGNALPRO

    if any(term in lowered for term in ("mbio signalpro", "mbio signal pro")):
        return MBIO_SIGNALPRO

    return AIOS_CORE
